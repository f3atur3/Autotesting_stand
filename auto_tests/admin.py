from django.contrib import admin
from .models import Test, TestType

@admin.register(TestType)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name', 'type_discription')
    list_display_links = ('id', 'type_name', 'type_discription')
    search_fields = ('id', 'type_name', 'type_discription')
    
@admin.register(Test)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_name', 'test_type')
    list_display_links = ('id', 'test_name', 'test_type')
    search_fields = ('id', 'test_name', 'test_type')
