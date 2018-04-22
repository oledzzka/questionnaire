from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView as BaseLoginView
from django.forms import Form, RadioSelect, ModelChoiceField
from django.shortcuts import resolve_url
from django.utils.decorators import method_decorator
from django.views.generic import ListView, FormView

from .models import Questionnaire, AnswersList, UserAnswer, Question


class LoginView(BaseLoginView):
    template_name = 'core/login.html'
    next = 'core:home'


class QuestionnaireListView(ListView):
    model = Questionnaire
    queryset = Questionnaire.objects.filter(show=True).order_by('-date')
    context_object_name = 'questionnaire_list'
    template_name = 'core/home.html'


class QuestionListForm(FormView):
    questionnaire = None
    question_list = None
    form_class = Form
    template_name = 'core/question_list.html'

    @method_decorator(login_required)
    def dispatch(self, request, pk=None, *args, **kwargs):
        self.questionnaire = Questionnaire.objects.filter(pk=pk).first()
        return super(QuestionListForm, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        form = super(QuestionListForm, self).get_form(form_class)
        if self.questionnaire is not None:
            for question in self.questionnaire.question_list.all():
                form.fields[str(question.id)] = ModelChoiceField(label=question.text,
                                                                 queryset=question.answer_list.all(),
                                                                 widget=RadioSelect(),
                                                                 empty_label=None,
                                                                 required=True)
        return form

    def get_context_data(self, **kwargs):
        context = super(QuestionListForm, self).get_context_data(**kwargs)
        context['questionnaire'] = self.questionnaire
        context['questionnaire_finished'] = False
        if UserAnswer.objects.filter(author=self.request.user,
                                     answer__question__questionnaire=self.questionnaire).exists():
            context['questionnaire_finished'] = True
            question_list = []
            for question in Question.objects.filter(questionnaire=self.questionnaire):
                query = UserAnswer.objects.filter(answer__question=question)
                count_all = query.count()
                if count_all != 0:
                    answer_list_percent = []
                    for answer in AnswersList.objects.filter(question=question):
                        answer_list_percent.append({'answer': answer,
                                                    'percent': ('%.2f' %
                                                                (query.filter(answer=answer).count() / count_all * 100))})
                    question_list.append({'question': question,
                                          'answer_list': answer_list_percent})
            context['question_list_percent'] = question_list
        return context

    def form_valid(self, form):
        for question in self.questionnaire.question_list.all():
            answer = UserAnswer()
            answer.author = self.request.user
            answer.answer = form.cleaned_data.get(str(question.id))
            answer.question = question
            answer.questionnaire = self.questionnaire
            answer.save()
        return super(QuestionListForm, self).form_valid(form)

    def get_success_url(self):
        return resolve_url('core:question_list', pk=self.questionnaire.id)
