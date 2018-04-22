from django.db import models
from django.contrib.auth.models import AbstractUser as BaseUser

from questionnaire import settings


class User(BaseUser):
    pass


class Questionnaire(models.Model):
    title = models.CharField(max_length=50, default='')
    show = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('date', )

    def __str__(self):
        return self.title


class Question(models.Model):
    questionnaire = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, related_name='question_list')
    text = models.TextField(default='')
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['my_order']

    def __str__(self):
        text = self.text.split('\n')[0]
        return text if len(text) <= 20 else text[:20]


class AnswersList(models.Model):
    text = models.CharField(max_length=100, default='')
    question = models.ForeignKey(Question, related_name='answer_list', on_delete=models.CASCADE)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ['my_order']

    def __str__(self):
        return self.text


class UserAnswer(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_DEFAULT, default=None)
    answer = models.ForeignKey(AnswersList, related_name='answer', on_delete=models.CASCADE)

    def __str__(self):
        return "answer:{answer}, User:{user}".format(answer=self.answer.text,
                                                     user=self.author)

