# Questions 12-20, 27, 29-38 and 42-50
import asyncio
import io
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils.text import slugify
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer

from .forms import CourseTopicForm
from .models import Answer
from .models import CourseTopic
from .models import GeneratedContent
from .models import Question
from .models import Quiz
from .models import Summary
from .services import ContentGenerationError
from .services import generate_course_material

logger = logging.getLogger(__name__)

@login_required
def generate_content(request):
    # Questions 12, 13 and 14
    if request.method == "POST":
        form = CourseTopicForm(
            request.POST,
        )

        if form.is_valid():
            topic_title = form.cleaned_data["title"]

            try:
                # Questions 15-18
                generated_data = asyncio.run(
                    generate_course_material(
                        topic_title,
                    )
                )

                # Questions 19, 27, 29 and 30
                with transaction.atomic():
                    topic = form.save(
                        commit=False,
                    )

                    topic.teacher = request.user
                    topic.save()

                    quiz_data = generated_data["quiz"]
                
                    quiz = Quiz.objects.create(
                        topic=topic,
                        title=quiz_data.get(
                            "title",
                            f"{topic.title} Quiz",
                        ),
                        description=quiz_data.get(
                            "description",
                            "",
                        ),
                    )

                    for question_data in quiz_data.get(
                        "questions",
                        [],
                    ):
                        question = Question.objects.create(
                            quiz=quiz,
                            question_text=question_data.get(
                                "questionText",
                                "Untitled question",
                            ),
                        )

                        for option_data in question_data.get(
                            "options",
                            [],
                        ):
                            Answer.objects.create(
                                question=question,
                                answer_text=option_data.get(
                                    "text",
                                    "Untitled option",
                                ),
                                is_correct=bool(
                                    option_data.get(
                                        "isCorrect",
                                        False,
                                    )
                                ),
                            )

                    key_points_text = "\n".join(
                        str(point)
                        for point in generated_data[
                            "keyPoints"
                        ]
                    )
                
                    GeneratedContent.objects.create(
                        topic=topic,
                        quiz=quiz,
                        notes=generated_data["notes"],
                        key_points=key_points_text,
                    )
                
                    Summary.objects.create(
                        topic=topic,
                        summary_text=generated_data[
                            "summary"
                        ],
                    )

                messages.success(
                    request,
                    "Course content generated successfully.",
                )

                # Question 20
                return redirect(
                    "view_content",
                    topic_id=topic.id,
                )
            
            except ContentGenerationError as exc:
                logger.exception(
                    "Content generation error."
                )

                messages.error(
                    request,
                    str(exc),
                )

            except Exception:
                logger.exception(
                    "Unexpected content generation error."
                )

                messages.error(
                    request,
                    "Unexpected error. Please try again.",
                )

    else:
        # Question 13
        form = CourseTopicForm()

    return render(
        request,
        "generator/generate_content.html",
        {
            "form": form,
        },
    )

def student_dashboard(request):
    # Question 31
    topics = CourseTopic.objects.select_related(
        "teacher",
    ).order_by(
        "-created_at",
    )

    return render(
        request,
        "generator/student_dashboard.html",
        {
            "topics": topics,
        },
    )

def view_content(request, topic_id):
    # Question 32
    topic = get_object_or_404(
        CourseTopic.objects.select_related(
            "teacher",
        ),
        id=topic_id,
    )

    generated_content = get_object_or_404(
        GeneratedContent,
        topic=topic,
    )

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            "questions__answers",
        ),
        topic=topic,
    )

    summary = get_object_or_404(
        Summary,
        topic=topic,
    )

    return render(
        request,
        "generator/view_content.html",
        {
            "topic": topic,
            "generated_content": generated_content,
            "key_points": (
                generated_content.get_key_points()
            ),
            "quiz": quiz,
            "summary": summary,
        },
    )

def submit_quiz(request, topic_id):
    # Questions 36, 37 and 38
    if request.method != "POST":
        return HttpResponseNotAllowed(
            [
                "POST",
            ]
        )

    topic = get_object_or_404(
        CourseTopic,
        id=topic_id,
    )

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            "questions__answers",
        ),
        topic=topic,
    )

    results = []
    score = 0
    questions = list(
        quiz.questions.all()
    )

    for question in questions:
        selected_id = request.POST.get(
            f"question_{question.id}"
        )

        selected_answer = None

        if selected_id:
            selected_answer = question.answers.filter(
                id=selected_id,
            ).first()

        correct_answer = question.answers.filter(
            is_correct=True,
        ).first()

        is_correct = bool(
            selected_answer
            and selected_answer.is_correct
        )

        if is_correct:
            score += 1

        results.append(
            {
                "question": question,
                "selected_answer": selected_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct,
            }
        )

    total = len(questions)

    percentage = (
        round(
            score / total * 100,
            2,
        )
        if total
        else 0
    )

    return render(
        request,
        "generator/quiz_result.html",
        {
            "topic": topic,
            "quiz": quiz,
            "results": results,
            "score": score,
            "total": total,
            "percentage": percentage,
        },
    )

def export_pdf(request, topic_id):
    # Questions 42 and 43
    topic = get_object_or_404(
        CourseTopic.objects.select_related(
            "teacher",
        ),
        id=topic_id,
    )

    generated_content = get_object_or_404(
        GeneratedContent,
        topic=topic,
    )

    quiz = get_object_or_404(
        Quiz.objects.prefetch_related(
            "questions__answers",
        ),
        topic=topic,
    )

    summary = get_object_or_404(
        Summary,
        topic=topic,
    )

    # Question 44
    pdf_buffer = io.BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CourseTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        spaceAfter=20,
    )

    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        spaceBefore=12,
        spaceAfter=8,
    )

    story = []

    # Question 45
    story.append(
        Spacer(
            1,
            4 * cm,
        )
    )

    story.append(
        Paragraph(
            escape_pdf(topic.title),
            title_style,
        )
    )

    story.append(
        Paragraph(
            (
                "Teacher: "
                + escape_pdf(
                    topic.teacher.get_username()
                )
            ),
            styles["Heading3"],
        )
    )

    story.append(
        PageBreak()
    )

    # Question 46
    story.append(
        Paragraph(
            "Summary",
            section_style,
        )
    )

    story.append(
        Paragraph(
            escape_pdf(summary.summary_text),
            styles["BodyText"],
        )
    )

    # Question 47
    story.append(
        Paragraph(
            "Notes",
            section_style,
        )
    )

    for paragraph in generated_content.notes.splitlines():
        if paragraph.strip():
            story.append(
                Paragraph(
                    escape_pdf(paragraph),
                    styles["BodyText"],
                )
            )

    # Question 48
    story.append(
        Paragraph(
            "Key Points",
            section_style,
        )
    )

    for point in generated_content.get_key_points():
        story.append(
            Paragraph(
                "• " + escape_pdf(point),
                styles["BodyText"],
            )
        )

    # Question 49
    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            escape_pdf(quiz.title),
            title_style,
        )
    )

    for number, question in enumerate(
        quiz.questions.all(),
        start=1,
    ):
        story.append(
            Paragraph(
                (
                    f"{number}. "
                    + escape_pdf(
                        question.question_text
                    )
                ),
                styles["Heading4"],
            )
        )

        for letter, answer in zip(
            [
                "A",
                "B",
                "C",
                "D",
                "E",
            ],
            question.answers.all(),
        ):
            story.append(
                Paragraph(
                    (
                        f"{letter}. "
                        + escape_pdf(
                            answer.answer_text
                        )
                    ),
                    styles["BodyText"],
                )
            )

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Correct Answers",
            title_style,
        )
    )

    for number, question in enumerate(
        quiz.questions.all(),
        start=1,
    ):
        correct_answer = question.answers.filter(
            is_correct=True,
        ).first()

        correct_text = (
            correct_answer.answer_text
            if correct_answer
            else "No correct answer"
        )

        story.append(
            Paragraph(
                (
                    f"{number}. "
                    + escape_pdf(correct_text)
                ),
                styles["BodyText"],
            )
        )

    document.build(
        story,
    )

    pdf_buffer.seek(0)

    filename = (
        slugify(topic.title)
        or "course-material"
    )

    # Question 50
    return FileResponse(
        pdf_buffer,
        as_attachment=True,
        filename=f"{filename}.pdf",
        content_type="application/pdf",
    )

def escape_pdf(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
