from django.contrib import admin

from .models import Question, Survey, Answer


class AnswerInline(admin.TabularInline):
    model = Answer


class QuestionInlines(admin.TabularInline):
    model = Question
    readonly_fields = ['pk', ]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['pk', 'answer']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['pk', 'question', 'survey']
    inlines = [AnswerInline, ]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'published']
    exclude = ['slug', 'created_at']
    inlines = [QuestionInlines, ]
