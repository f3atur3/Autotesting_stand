from django.contrib import admin
from auto_tests.views import Index, TestTypes, Tests, CustomLoginView, CustomLogoutView, ViewTests, ViewTestsByCat, ViewTestsByTest
from analysis.views import Results, DetailResult, HistoryResult, DeatailStreamResult
from django.urls import path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Index.as_view(), name='index'),
    path('test_types', TestTypes.as_view(), name='test_types'),
    path('tests', Tests.as_view(), name='tests'),
    path('results', Results.as_view(), name='results'),
    path('detail_result/<int:pk>', DetailResult.as_view(), name='detail_result'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('history_result/<int:pk>', HistoryResult.as_view(), name='history_result'),
    path('view_tests', ViewTests.as_view(), name="view_tests"),
    path('results_test/<int:pk>', DeatailStreamResult.as_view(), name='results_test'),
    path('results_test/cat/<int:pk>', ViewTestsByCat.as_view(), name="results_test_by_cat"),
    path('results_test/test/<int:pk>', ViewTestsByTest.as_view(), name="results_test_by_test"),
]
