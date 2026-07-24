# Questions 51, 52, 53 and 54
from unittest.mock import AsyncMock
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Answer
from .models import CourseTopic
from .models import GeneratedContent
from .models import Question
from .models import Quiz
from .models import Summary

class ModelTests(TestCase):
    # Question 51
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            password="Teacher@123",
        )

        self.topic = CourseTopic.objects.create(
            title="Python Basics",
            teacher=self.teacher,
        )

        self.quiz = Quiz.objects.create(
            topic=self.topic,
            title="Python Quiz",
            description="Basic quiz",
        )

        self.content = GeneratedContent.objects.create(
            topic=self.topic,
            quiz=self.quiz,
            notes="Python notes",
            key_points="Readable\nSimple",
        )

        self.summary = Summary.objects.create(
            topic=self.topic,
            summary_text="Python summary",
        )

        self.question = Question.objects.create(
            quiz=self.quiz,
            question_text="What is Python?",
        )

        self.answer = Answer.objects.create(
            question=self.question,
            answer_text="Programming language",
            is_correct=True,
        )

    def test_create_objects(self):
        self.assertEqual(
            CourseTopic.objects.count(),
            1,
        )

        self.assertEqual(
            GeneratedContent.objects.count(),
            1,
        )

        self.assertEqual(
            Quiz.objects.count(),
            1,
        )

        self.assertEqual(
            Question.objects.count(),
            1,
        )

        self.assertEqual(
            Answer.objects.count(),
            1,
        )

    def test_update_topic(self):
        self.topic.title = "Advanced Python"
        self.topic.save()
        self.topic.refresh_from_db()

        self.assertEqual(
            self.topic.title,
            "Advanced Python",
        )

    def test_delete_topic(self):
        self.topic.delete()

        self.assertEqual(
            Quiz.objects.count(),
            0,
        )

        self.assertEqual(
            Question.objects.count(),
            0,
        )

        self.assertEqual(
            Answer.objects.count(),
            0,
        )

class ViewTests(TestCase):
    # Question 52
    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            password="Teacher@123",
        )

    @patch(
        "generator.views.generate_course_material",
        new_callable=AsyncMock,
    )
    def test_generate_content_saves_data(
        self,
        mock_generate,
    ):
        mock_generate.return_value = {
            "notes": "Generated notes",
            "keyPoints": [
                "Point one",
                "Point two",
            ],
            "summary": "Generated summary",
            "quiz": {
                "title": "Generated quiz",
                "description": "Description",
                "questions": [
                    {
                        "questionText": "Sample question?",
                        "options": [
                            {
                                "text": "Correct",
                                "isCorrect": True,
                            },
                            {
                                "text": "Wrong 1",
                                "isCorrect": False,
                            },
                            {
                                "text": "Wrong 2",
                                "isCorrect": False,
                            },
                            {
                                "text": "Wrong 3",
                                "isCorrect": False,
                            },
                        ],
                    }
                ],
            },
        }

        self.client.login(
            username="teacher",
            password="Teacher@123",
        )

        response = self.client.post(
            reverse("generate_content"),
            {
                "title": "Django Testing",
            },
        )

        topic = CourseTopic.objects.get(
            title="Django Testing",
        )

        self.assertRedirects(
            response,
            reverse(
                "view_content",
                kwargs={
                    "topic_id": topic.id,
                },
            ),
        )

        self.assertTrue(
            Summary.objects.filter(
                topic=topic,
            ).exists()
        )

    def test_export_pdf(self):
        topic = CourseTopic.objects.create(
            title="PDF Topic",
            teacher=self.teacher,
        )

        quiz = Quiz.objects.create(
            topic=topic,
            title="PDF Quiz",
            description="PDF quiz",
        )

        GeneratedContent.objects.create(
            topic=topic,
            quiz=quiz,
            notes="PDF notes",
            key_points="Point one\nPoint two",
        )

        Summary.objects.create(
            topic=topic,
            summary_text="PDF summary",
        )

        question = Question.objects.create(
            quiz=quiz,
            question_text="PDF question?",
        )

        Answer.objects.create(
            question=question,
            answer_text="Correct answer",
            is_correct=True,
        )

        response = self.client.get(
            reverse(
                "export_pdf",
                kwargs={
                    "topic_id": topic.id,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertEqual(
            response["Content-Type"],
            "application/pdf",
        )

class FixtureTests(TestCase):
    # Question 53
    fixtures = [
        "sample_data.json",
    ]

    def test_fixture_loaded(self):
        self.assertGreaterEqual(
            CourseTopic.objects.count(),
            1,
        )
