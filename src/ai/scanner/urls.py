from django.urls import include, path

from .views import PageTwo

urlpatterns = [
    path('echo/', PageTwo.as_view()),
]
