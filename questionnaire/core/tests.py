from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from core.models import Questionnaire, Question, User, AnswersList, UserAnswer


class QuestionnaireListTest(TestCase):

    def setUp(self):
        super(QuestionnaireListTest, self).setUp()
        Questionnaire.objects.create(title="1", show=True)
        Questionnaire.objects.create(title="1", show=False)
        Questionnaire.objects.create(title="1", show=True)
        self.response = self.client.get(reverse("core:home"))

    def test_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_count_questionnaire_show(self):
        self.assertEqual(len(self.response.context['questionnaire_list']), 2)


class QuestionViewTestAnonymous(TestCase):

    def setUp(self):
        super(QuestionViewTestAnonymous, self).setUp()
        self.questionnaire = Questionnaire.objects.create(title='1', show=True)
        Question.objects.create(questionnaire=self.questionnaire)

    def test_anonymous_user(self):
        url = reverse('core:question_list', kwargs={'pk': self.questionnaire.id})
        response = self.client.get(url)
        self.assertRedirects(response, "{url_login}?next={next}".format(url_login=reverse("core:login"),
                                                                        next=url))


class QuestionViewTestErrorQuestionnaire(TestCase):

    def setUp(self):
        super(QuestionViewTestErrorQuestionnaire, self).setUp()
        self.current_user = User.objects.create(username='test_user', email='test_user@mail.ru')
        self.client.force_login(self.current_user)

    def test_get_error_question(self):
        with self.assertRaises(NoReverseMatch):
            self.client.get(reverse('core:question_list', kwargs={'pk': '1'}))


class QuestionViewTestUserUnfinished(TestCase):
    def setUp(self):
        super(QuestionViewTestUserUnfinished, self).setUp()
        self.questionnaire = Questionnaire.objects.create(title='1', show=True)
        self.question = Question.objects.create(questionnaire=self.questionnaire)
        self.answer = AnswersList.objects.create(question=self.question)
        self.current_user = User.objects.create(username='test_user', email='test_user@mail.ru')
        self.client.force_login(self.current_user)
        self.response = self.client.get(reverse('core:question_list',
                                                kwargs={'pk': self.questionnaire.id}))

    def test_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_questionnaire(self):
        self.assertEqual(self.response.context['questionnaire'].title, self.questionnaire.title)

    def test_finished(self):
        self.assertFalse(self.response.context['questionnaire_finished'])

    def test_create_answer(self):
        csrf = self.response.context['csrf_token']
        self.client.post(reverse('core:question_list', kwargs={'pk': self.questionnaire.id}),
                                                {'csrf_token': csrf, str(self.question.id): [str(self.answer.id)]})
        self.assertEqual(len(UserAnswer.objects.all()), 1)


class QuestionViewTestUserFinished(TestCase):
    def setUp(self):
        super(QuestionViewTestUserFinished, self).setUp()
        self.questionnaire = Questionnaire.objects.create(title='1', show=True)
        self.question = Question.objects.create(questionnaire=self.questionnaire)
        self.answer = AnswersList.objects.create(question=self.question)
        self.current_user = User.objects.create(username='test_user', email='test_user@mail.ru')
        UserAnswer.objects.create(author=self.current_user, answer=self.answer)
        fake_questionnaire = Questionnaire.objects.create(title='fake', show=True)
        fake_question = Question.objects.create(questionnaire=fake_questionnaire)
        fake_answer = AnswersList.objects.create(question=fake_question)
        UserAnswer.objects.create(author=self.current_user, answer=fake_answer)
        self.client.force_login(self.current_user)
        self.response = self.client.get(reverse('core:question_list',
                                                kwargs={'pk': self.questionnaire.id}))

    def test_status(self):
        self.assertEqual(self.response.status_code, 200)

    def test_questionnaire(self):
        self.assertEqual(self.response.context['questionnaire'].title, self.questionnaire.title)

    def test_finished(self):
        self.assertTrue(self.response.context['questionnaire_finished'])

    def test_question_list_percent(self):
        self.assertEqual(len(self.response.context['question_list_percent']), 1)

    def test_question(self):
        self.assertEqual(self.response.context['question_list_percent'][0]['question'], self.question)

    def test_answer_list(self):
        self.assertEqual(len(self.response.context['question_list_percent'][0]['answer_list']), 1)

    def test_answer(self):
        answer = self.response.context['question_list_percent'][0]['answer_list'][0]['answer']
        self.assertEqual(answer, self.answer)


class SendAnswerSignalTest(TestCase):

    def setUp(self):
        super(SendAnswerSignalTest, self).setUp()
        self.questionnaire = Questionnaire.objects.create(title='1', show=True)
        self.question = Question.objects.create(questionnaire=self.questionnaire)
        self.answer1 = AnswersList.objects.create(question=self.question)
        self.answer2 = AnswersList.objects.create(question=self.question)
        self.current_user = User.objects.create(username='test_user', email='test_user@mail.ru')
        UserAnswer.objects.create(author=self.current_user, answer=self.answer1)

    def test_repeated_send(self):
        UserAnswer.objects.create(author=self.current_user, answer=self.answer2)
        self.assertEqual(len(UserAnswer.objects.filter(author=self.current_user,
                                                       answer__question=self.question)), 1)

    def test_other_user_send(self):
        user2 = User.objects.create(username='test_user2', email='test@test.test')
        UserAnswer.objects.create(author=user2, answer=self.answer1)
        self.assertEqual(len(UserAnswer.objects.filter(answer__question=self.question)), 2)

    def test_other_question(self):
        question2 = Question.objects.create(questionnaire=self.questionnaire)
        answer = AnswersList.objects.create(question=question2)
        UserAnswer.objects.create(author=self.current_user,
                                  answer=answer)
        self.assertEqual(len(UserAnswer.objects.filter(answer__question__questionnaire=self.questionnaire,
                                                       author=self.current_user)), 2)


class TestPercent(TestCase):

    def setUp(self):
        super(TestPercent, self).setUp()
        self.questionnaire = Questionnaire.objects.create(title='1', show=True)
        self.question = Question.objects.create(questionnaire=self.questionnaire)
        self.answer = AnswersList.objects.create(question=self.question)
        self.current_user = User.objects.create(username='test_user', email='test_user@mail.ru')
        UserAnswer.objects.create(author=self.current_user, answer=self.answer)
        self.client.force_login(self.current_user)

    def test_one_answer(self):
        response = self.client.get(reverse('core:question_list',
                                           kwargs={'pk': self.questionnaire.id}))
        percent = response.context['question_list_percent'][0]['answer_list'][0]['percent']
        self.assertEqual(percent, '{:.2f}'.format(100))

    def test_delete_answer(self):
        answer2 = AnswersList.objects.create(question=self.question)
        answer3 = AnswersList.objects.create(question=self.question)
        user2 = User.objects.create(username='test_user2', email='test_user@mail.ru')
        user3 = User.objects.create(username='test_user3', email='test_user@mail.ru')
        UserAnswer.objects.create(author=user2, answer=answer2)
        UserAnswer.objects.create(author=user3, answer=answer3)
        response = self.client.get(reverse('core:question_list',
                                           kwargs={'pk': self.questionnaire.id}))
        percent = response.context['question_list_percent'][0]['answer_list'][0]['percent']
        self.assertEqual(percent, '{:.2f}'.format(33.333))
