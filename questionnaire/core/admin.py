import nested_admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Questionnaire, Question, UserAnswer, AnswersList

class UserAdmin(BaseUserAdmin):
    pass


class ToAnswerListInline(nested_admin.NestedTabularInline):
    model = AnswersList
    extra = 0
    sortable_field_name = 'my_order'


class ToQuestionInline(nested_admin.NestedTabularInline):
    model = Question
    extra = 0
    inlines = [ToAnswerListInline]
    sortable_field_name = 'my_order'


@admin.register(Questionnaire)
class TableQuestionnaire(nested_admin.NestedModelAdmin):
    inlines = [ToQuestionInline]

admin.site.register(UserAnswer)
admin.site.register(User)
