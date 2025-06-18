from django.contrib import admin
from .models import Problem, TestCase, Submission

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty', 'company', 'created_at']
    list_filter = ['difficulty', 'company', 'created_at']
    search_fields = ['title', 'tags']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'difficulty', 'company', 'tags')
        }),
        ('Problem Description', {
            'fields': ('statement', 'input_format', 'output_format')
        }),
        ('Sample Data', {
            'fields': ('sample_input', 'sample_output')
        }),
    )

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ['problem', 'is_sample', 'input_preview', 'expected_preview']
    list_filter = ['is_sample', 'problem__difficulty']
    search_fields = ['problem__title']
    
    def input_preview(self, obj):
        return obj.input_data[:50] + "..." if len(obj.input_data) > 50 else obj.input_data
    input_preview.short_description = "Input Preview"
    
    def expected_preview(self, obj):
        return obj.expected_output[:50] + "..." if len(obj.expected_output) > 50 else obj.expected_output
    expected_preview.short_description = "Expected Output Preview"

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'problem', 'language', 'verdict', 'submitted_at']
    list_filter = ['language', 'verdict', 'submitted_at']
    search_fields = ['user__username', 'problem__title']
    readonly_fields = ['submitted_at']
    ordering = ['-submitted_at']
    
    def has_add_permission(self, request):
        return False  # Submissions should only be created through the interface
