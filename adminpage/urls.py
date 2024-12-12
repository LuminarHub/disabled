from django.urls import path
from .views import *

urlpatterns = [
    path('adminhomepage/',AdminHome.as_view(),name='ah'),
    path('faculties/',FacultyList.as_view(),name='faculty'),
    path('students/',StudentsList.as_view(),name='students'),
]
