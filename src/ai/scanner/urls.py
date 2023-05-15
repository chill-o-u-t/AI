from django.urls import include, path

from .views import PageTwo, PageThree

urlpatterns = [
    path('page_2/', PageTwo.as_view()),
    path('page_3/', PageThree.as_view())
]
