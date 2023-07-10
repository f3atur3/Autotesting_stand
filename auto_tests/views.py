import json
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.detail import DetailView
from django.db.models.query import QuerySet
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from .models import TestType, Test
from .forms import CustomLoginForm


class Index(TemplateView):
    template_name = "auto_tests/index.html"

class TestTypes(LoginRequiredMixin, ListView):
    template_name = "auto_tests/test_type.html"
    context_object_name = "types"
    login_url = '/login/'
    
    def get_queryset(self) -> QuerySet[Any]:
        return TestType.objects.all() 
    
class Tests(LoginRequiredMixin, TemplateView):
    template_name = "auto_tests/tests.html"
    login_url = '/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cats"] = {
            cat: Test.objects.filter(test_type=cat)
            for cat in TestType.objects.all()
        }
        return context
    
    
#Класс обработчика выхода из системы
class CustomLogoutView(LogoutView):
    next_page = '/'

#Класс обработчика входа в систему
class CustomLoginView(LoginView):
    template_name = 'auto_tests/login.html'
    form_class = CustomLoginForm
    
    def get_success_url(self):
        return self.request.GET.get('next', '/')
    
class ViewTests(LoginRequiredMixin, TemplateView):
    template_name = "auto_tests/view_tests.html"
    login_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pks"] = [test.pk for test in Test.objects.all()]
        context["names"] = [test.test_name for test in Test.objects.all()]
        return context

class ViewTestsByCat(LoginRequiredMixin, DetailView):
    template_name = "auto_tests/view_tests.html"
    model = TestType
    login_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pks"] = [test.pk for test in Test.objects.filter(test_type=self.object)]
        context["names"] = [test.test_name for test in Test.objects.filter(test_type=self.object)]
        return context

class ViewTestsByTest(LoginRequiredMixin, DetailView):
    template_name = "auto_tests/view_tests.html"
    model = Test
    login_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["pks"] = [self.object.pk]
        context["names"] = [self.object.test_name]
        return context