"""collectanea URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import notifications.urls
from django.conf.urls import url
from .views import HomeView
urlpatterns = [
    path("",HomeView.as_view()),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/auth/', include('accounts.urls')),
    path('api/questions/', include('questions.urls')),
    path('moderator/', include('moderatorpanel.urls')),
    path('adminpanel/', include('adminpanel.urls')),
    path('api/answers/', include('answers.urls')),
    path('api/misc/', include('misc.urls')),
    
    url('^inbox/notifications/', include(notifications.urls, namespace='notifications')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

