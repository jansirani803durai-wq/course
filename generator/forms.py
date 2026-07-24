# Question 11
from django import forms
from .models import CourseTopic

class CourseTopicForm(forms.ModelForm):
    class Meta:
        model = CourseTopic
        fields = [
            "title",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Example: Introduction to Python",
                }
            ),
        }
