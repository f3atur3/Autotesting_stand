from django.db import models
from auto_tests.models import Test

class Result(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE,
                                  verbose_name="Тест")
    passed = models.BooleanField(verbose_name="Пройден")
    test_error = models.TextField(null=True, blank=True, verbose_name="Ошибка теста")
    server_timeout = models.DurationField(verbose_name="Время ответа сервера")
    date = models.DateTimeField(verbose_name="Дата прохождения теста")
    
    class Meta:
        verbose_name_plural = 'Результаты'
        verbose_name = 'Результат'
