from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout
from .views import QuestionnaireListView, LoginView, QuestionListForm, QuestionnaireView

urlpatterns = [
    url(r'^$', QuestionnaireListView.as_view(), name='home'),
    url(r'^login', LoginView.as_view(), name='login'),
    url(r'^logout', logout, name='logout'),
    url(r'^question_list/(?P<pk>\d+)/', login_required(QuestionListForm.as_view()), name='question_list'),
]
