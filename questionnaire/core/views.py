from django.contrib.auth.views import LoginView as BaseLoginView
from django.views.generic import ListView

from .models import Questionnaire


class LoginView(BaseLoginView):
    template_name = 'core/login.html'
    next = 'core:home'


class QuestionnaireListView(ListView):
    model = Questionnaire
    queryset = Questionnaire.objects.filter(show=True).order_by('-date')
    context_object_name = 'questionnaire_list'
    template_name = 'core/home.html'
