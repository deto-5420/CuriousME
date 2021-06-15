from django.urls import path,include

from .views import (
                     FlagAnswer, WriteAnswer,WriteReplies,
                    GetAnswers, ReactAnswers,GetLatestAnswer,GetReplies,GetMyAnswersReply, DeleteAnswer, DeleteReply,SubmitPoll
                )
from rest_framework import routers


# router = routers.SimpleRouter(trailing_slash=False)
# router.register(r'webhooks', HookViewSet, 'webhook')


urlpatterns = [
    path('flag-answer/', FlagAnswer.as_view(), name="FlagAnswer"),
    # path('add-tip/', AddTip.as_view(), name="AddTip"),
    path('write-answer/', WriteAnswer.as_view(), name="WriteAnswer"),
    path('write-reply/', WriteReplies.as_view(), name="WriteReplies"),
    path('get-answers/', GetAnswers.as_view(), name="GetAnswers"),
    path('get-replies/', GetReplies.as_view(), name="GetReplies"),
    path('delete-answer/', DeleteAnswer.as_view(), name="DeleteAnswer"),
    path('delete-replies/', DeleteReply.as_view(), name="DeleteReply"),
    path('get-my-answers-reply/', GetMyAnswersReply.as_view(), name="GetMyAnswersReply"),
    path('submit-poll/', SubmitPoll.as_view(), name="SubmitPoll"),
    path('react-answers/', ReactAnswers.as_view(), name="ReactAnswers"),
    path('reciever/', GetLatestAnswer.as_view(), name="GetLatestAnswer"),
]

# urlpatterns += router.urls