from django.shortcuts import render
from django.views.generic import TemplateView
from accounts.models import *
# Create your views here.


class AdminHome(TemplateView):
    template_name='admin_home.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty'] = Faculty.objects.all()[:5]
        context['students'] = Student.objects.all()[:5]
        return context

class FacultyList(TemplateView):
    template_name='faculty_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['faculty'] = Faculty.objects.all()
        return context

class StudentsList(TemplateView):
    template_name='students_list.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['students'] = Student.objects.all()
        return context