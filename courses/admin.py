from django.contrib import admin
from .models import Theme, Curriculum, Lesson, LessonCompletion

admin.site.register(Theme)
admin.site.register(Curriculum)
admin.site.register(Lesson)
admin.site.register(LessonCompletion)
