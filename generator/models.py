# Questions 6, 7, 21, 22, 23, 24 and 28
from django.contrib.auth.models import User
from django.db import models

class CourseTopic(models.Model):
    # Question 6
    title = models.CharField(
        max_length=200,
    )

    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="course_topics",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.title

class Quiz(models.Model):
    # Question 21
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    def __str__(self):
        return self.title

class GeneratedContent(models.Model):
    # Questions 7 and 24
    topic = models.OneToOneField(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="generated_content",
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.SET_NULL,
        related_name="generated_contents",
        null=True,
        blank=True,
    )

    notes = models.TextField()
    key_points = models.TextField()

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    def get_key_points(self):
        return [
            point.strip()
            for point in self.key_points.splitlines()
            if point.strip()
        ]

    def __str__(self):
        return f"Content for {self.topic.title}"

class Question(models.Model):
    # Question 22
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    question_text = models.TextField()

    def __str__(self):
        return self.question_text[:80]

class Answer(models.Model):
    # Question 23
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    answer_text = models.CharField(
        max_length=500,
    )

    is_correct = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.answer_text

class Summary(models.Model):
    # Question 28
    topic = models.OneToOneField(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name="summary",
    )

    summary_text = models.TextField()

    def __str__(self):
        return f"Summary for {self.topic.title}"
