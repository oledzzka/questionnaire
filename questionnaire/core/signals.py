from core.models import UserAnswer
from django.db.models.signals import pre_save


def pre_save_user_answer_signal(sender, instance, *args, **kwargs):
    if isinstance(instance, UserAnswer):
        query = UserAnswer.objects.filter(author=instance.author,
                                          answer__question=instance.answer.question)
        if len(query) > 0:
            for user_answer in query:
                user_answer.delete()

pre_save.connect(pre_save_user_answer_signal, UserAnswer)