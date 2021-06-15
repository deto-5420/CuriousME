from django.urls import path,include

from .keywords_views import (
                AddKeyword, SearchKeywords, GetCategories, getPopularKeyword,SearchCategory
            )

from .views import (
                  AddBookmark, GetAllBookmarks,
                SearchQuestions, GetQuestionByAnswer,
                SuggestQuestions, ReactionQuestion, GetQuestionsByCategory,GetQuestionsByKeyword, myFeed, LikeQuestion,GetQuestionByID,getdownloadBook
            )

app_name = 'questions'

urlpatterns = [
    # Keywords urls
    path('add-keywords/', AddKeyword.as_view(), name="AddKeyword"),
    path('search-keyword/', SearchKeywords.as_view(), name="SearchKeywords"),
    path('search-category/', SearchCategory.as_view(), name="SearchCategory"),
    path('get-popular-keyword/', getPopularKeyword.as_view(), name="getPopularKeyword"),

    # Categories
    path('get-categories/', GetCategories.as_view(), name="GetCategories"),

    # Questions
    # path('post-question/', PostQuestion.as_view(), name="PostQuestion"),
    # path('delete-question/', DeleteQuestion.as_view(), name="DeleteQuestion"),
    # path('edit-question/', EditQuestion.as_view(), name="EditQuestion"),
    # path('get-my-questions/', GetMyQuestions.as_view(), name="GetMyQuestions"),

    # Bookmarks
    path('add-bookmarks/', AddBookmark.as_view(), name="AddBookmark"),
    path('get-all-bookmarks/', GetAllBookmarks.as_view(), name="GetAllBookmarks"),

    # Search
    path('search-questions/', SearchQuestions.as_view(), name="SearchQuestions"),

    # Answer
    path('get-question-by-answer/', GetQuestionByAnswer.as_view(), name="GetQuestionByAnswer"),

    path('get-question-by-id/', GetQuestionByID.as_view(), name="GetQuestionByID"),

    # Suggest questions
    path('suggest-questions/', SuggestQuestions.as_view(), name="SuggestQuestions"),

    # UpVote/DownVote Questions 
    #path('upvote-question/', UpVoteQuestion.as_view(), name="upvoteQuestion"),
    path('category-question/', GetQuestionsByCategory.as_view(), name="categoryQuestion"),

    path('like-question/', LikeQuestion.as_view(), name = 'LikeQuestion'),
    path('reaction-question/', ReactionQuestion.as_view(), name = 'ReactionQuestion'),
    path('keyword-question/', GetQuestionsByKeyword.as_view(), name = 'GetQuestionsByKeyword'),
    path('my-Feed/', myFeed.as_view(), name = 'myFeed'),
    path('get-download-book/', getdownloadBook.as_view(), name = 'getdownloadBook')
]