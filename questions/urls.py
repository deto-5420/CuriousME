from django.urls import path,include

from .keywords_views import (
                AddKeyword, SearchKeywords, GetCategories, 
            )

from .views import (
                PostQuestion, DeleteQuestion, EditQuestion, 
                GetMyQuestions, AddBookmark, GetAllBookmarks,
                SearchQuestions, GetQuestionByAnswer,
                SuggestQuestions, LikeQuestion
            )

app_name = 'questions'

urlpatterns = [
    # Keywords urls
    path('add-keywords/', AddKeyword.as_view(), name="AddKeyword"),
    path('search-keyword/', SearchKeywords.as_view(), name="SearchKeywords"),

    # Categories
    path('get-categories/', GetCategories.as_view(), name="GetCategories"),

    # Questions
    path('post-question/', PostQuestion.as_view(), name="PostQuestion"),
    path('delete-question/', DeleteQuestion.as_view(), name="DeleteQuestion"),
    path('edit-question/', EditQuestion.as_view(), name="EditQuestion"),
    path('get-my-questions/', GetMyQuestions.as_view(), name="GetMyQuestions"),

    # Bookmarks
    path('add-bookmarks/', AddBookmark.as_view(), name="AddBookmark"),
    path('get-all-bookmarks/', GetAllBookmarks.as_view(), name="GetAllBookmarks"),

    # Search
    path('search-questions/', SearchQuestions.as_view(), name="SearchQuestions"),

    # Answer
    path('get-question-by-answer/', GetQuestionByAnswer.as_view(), name="GetQuestionByAnswer"),

    # Suggest questions
    path('suggest-questions/', SuggestQuestions.as_view(), name="SuggestQuestions"),

    # UpVote/DownVote Questions 
    # path('upvote-question/', UpVoteQuestion.as_view(), name="upvoteQuestion"),
    # path('downvote-question/', DownVoteQuestion.as_view(), name="downvoteQuestion"),

    #Like Questions
    path('like-question/', LikeQuestion.as_view(), name = 'LikeQuestion')
]