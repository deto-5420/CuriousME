from django.urls import path,include
from .views import get_user_liked_Question_View, get_user_liked_Answer_View, get_user_liked_replies_View, ReportIssueView, getNotification,getProfessionList ,getUsersList,getQuesList


urlpatterns = [

    path('liked_Question/', get_user_liked_Question_View.as_view(), name="LikedQuestion"),
    path('liked_Answer/', get_user_liked_Answer_View.as_view(), name="LikedAnswer"),
    path('liked_replies/', get_user_liked_replies_View.as_view(), name="LikedReply"),
    path('report-issue/', ReportIssueView.as_view(), name="ReportIssueView"),
    path('get-notification/', getNotification.as_view(), name="getNotification"),
    path('get-profession/', getProfessionList.as_view(), name="getNotification"),
    path('get-users/', getUsersList.as_view(), name="getUsersList"),
    path('get-ques/', getQuesList.as_view(), name="getQuesList"),
]