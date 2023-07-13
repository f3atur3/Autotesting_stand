import locale
import time
from typing import Any, Dict
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.views.generic.detail import DetailView
from django.db.models import OuterRef, Subquery, TextField, BooleanField, DurationField, DateTimeField
from auto_tests.models import TestType
from .models import Result
from auto_tests.models import Test
from io import BytesIO
import base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from django.http import JsonResponse
from auto_tests.dss_tests.tests import CheckSignDocuments, CheckVerifySignature
from django.views.generic.base import TemplateView


class Results(LoginRequiredMixin, TemplateView):
    template_name = "analysis/results.html"
    login_url = '/login/'
    
    def get_queryset(self) -> QuerySet[Any]:
        subquery = Result.objects.filter(test_id=OuterRef('pk')).order_by('-date')
        
        queryset = Test.objects.annotate(
            latest_result_passed=Subquery(subquery.values('passed')[:1], output_field=BooleanField()),
            latest_result_test_error=Subquery(subquery.values('test_error')[:1], output_field=TextField()),
            latest_result_server_timeout=Subquery(subquery.values('server_timeout')[:1], output_field=DurationField()),
            latest_result_date=Subquery(subquery.values('date')[:1], output_field=DateTimeField())
        )
        
        return queryset
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        subquery = Result.objects.filter(test_id=OuterRef('pk')).order_by('-date')
        queryset = Test.objects.annotate(
            latest_result_passed=Subquery(subquery.values('passed')[:1], output_field=BooleanField()),
            latest_result_test_error=Subquery(subquery.values('test_error')[:1], output_field=TextField()),
            latest_result_server_timeout=Subquery(subquery.values('server_timeout')[:1], output_field=DurationField()),
            latest_result_date=Subquery(subquery.values('date')[:1], output_field=DateTimeField())
        )
        context["cats"] = {
            cat: queryset.filter(test_type=cat)
            for cat in TestType.objects.all()
        }
        return context
        

class HistoryResult(LoginRequiredMixin, DetailView):
    template_name = "analysis/history_result.html"
    context_object_name = "history_result"
    model = Test
    login_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['history'] = Result.objects.filter(test=self.object).order_by("date")
        return context
    
class DeatailStreamResult(LoginRequiredMixin, DetailView):
    model = Test
    login_url = '/login/'
    
    def render_to_response(self, context, **response_kwargs):
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        object = context['object']
        time.sleep(1)
        if object.meta_data["type"] == "sign":
            result = CheckSignDocuments(**object.meta_data, test=object).run()
        elif object.meta_data["type"] == "verify":
            result = CheckVerifySignature(**object.meta_data, test=object).run()
        time.sleep(1)
        # Сериализуйте объект в JSON
        serialized_object = {
            'test': result.test.__str__(),
            'passed': result.passed,
            'test_error': result.test_error,
            'server_timeout': result.server_timeout.__str__(),
            'date': result.date.strftime("%e %B %Y г. %H:%M"),
        }
        # Верните JSON-ответ
        return JsonResponse(serialized_object)
    
class DeatailTestJSON(LoginRequiredMixin, DetailView):
    model = Test
    login_url = '/login/'
    
    def render_to_response(self, context, **response_kwargs):
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
        object = context['object']
        # Сериализуйте объект в JSON
        serialized_object = {
            'test_name': object.test_name,
        }
        # Верните JSON-ответ
        return JsonResponse(serialized_object)

class DetailResult(LoginRequiredMixin, DetailView):
    template_name = "analysis/detail_result.html"
    context_object_name = "detail_result"
    model = Test
    login_url = '/login/'
    
    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
                
        results = Result.objects.filter(test=self.object).order_by("date")
        last_result = Result.objects.filter(test=self.object).order_by("-date").only()
        
        if results is None:
            context['last_result'] = None
            context['graph_image'] = None
            return context
        
        context['last_result'] = last_result
        
        # Создание списков для хранения значений server_timeout, date и passed
        server_timeouts = []
        dates = []
        passed_values = []
        
        # Заполнение списков данными из модели Result
        for result in results:
            server_timeouts.append(result.server_timeout.total_seconds())
            dates.append(result.date)
            passed_values.append(result.passed)
        
        # Создание графика Seaborn
        sns.set(style="whitegrid")
        plt.figure(figsize=(8, 6))
        
        # Построение точечного графика с цветовым отображением в зависимости от значения passed
        scatterplot = sns.scatterplot(x=dates, y=server_timeouts, hue=passed_values,
                                    palette={True: 'green', False: 'red'}, s=100)
        scatterplot.plot(dates, server_timeouts, color='grey')
        scatterplot.axhline(y=self.object.server_timeout.total_seconds(), color='red', linestyle='dashed')

        # Настройка осей и меток
        plt.xlabel('Дата прохождения теста')
        plt.ylabel('Время ответа сервера')

        # Добавление легенды
        legend_labels = ['Пройден', 'Не пройден']
        legend_colors = ['green', 'red']
        legend_markers = [plt.Line2D([0], [0], marker='o', color=color, linestyle='', markersize=8) for color in legend_colors]
        scatterplot.legend(legend_markers, legend_labels, title='Проверка')
        scatterplot.set_xticklabels(scatterplot.get_xticklabels(), rotation=45)
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Convert the buffer data to base64
        image_data = base64.b64encode(buf.read()).decode('utf-8')

        # Close the figure to free up memory
        plt.close()
        
        context['graph_image'] = image_data
        
        return context