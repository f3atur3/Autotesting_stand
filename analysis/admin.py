from django.contrib import admin
from .models import Result

@admin.register(Result)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'test', 'passed', 'date')
    list_display_links = ('id', 'test', 'passed', 'date')
    search_fields = ('id', 'test', 'passed', 'date')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
