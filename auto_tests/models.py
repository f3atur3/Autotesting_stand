from django.db import models
from datetime import timedelta

class TestType(models.Model):
    type_name = models.CharField(max_length=50, verbose_name="Название")
    type_discription = models.TextField(verbose_name="Описание")
    
    def __str__(self):
        return self.type_name
    
    class Meta:
        verbose_name_plural = 'Типы тестов'
        verbose_name = 'Тип'


class Test(models.Model):
    test_type = models.ForeignKey(TestType, on_delete=models.RESTRICT,
                                  verbose_name="Тип")
    test_name = models.CharField(max_length=50, verbose_name="Название")
    test_description = models.TextField(default="Описание отсутствует", verbose_name="Описание")
    server_timeout = models.DurationField(default=timedelta(milliseconds=400),
                                          verbose_name="Ожидаемое время ответа сервера")
    meta_data = models.JSONField(verbose_name="Мета данные (см. описание типа)")
    
    def __str__(self):
        return f'"{self.test_name}"'
    
    class Meta:
        verbose_name_plural = 'Тесты'
        verbose_name = 'Тест'