# Question 8
from django.contrib import admin
from .models import Answer
from .models import CourseTopic
from .models import GeneratedContent
from .models import Question
from .models import Quiz
from .models import Summary

admin.site.register(CourseTopic)
admin.site.register(GeneratedContent)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Summary)
