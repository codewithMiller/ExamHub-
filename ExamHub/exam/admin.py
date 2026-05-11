from django.contrib import admin
from .models import Exam, Question, ExamAttempt, StudentAnswer

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['title', 'question_count', 'duration_minutes', 'is_active', 'created_at']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['exam', 'order', 'text', 'correct_answer']
    list_filter = ['exam']

@admin.register(ExamAttempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'exam', 'score', 'total', 'percentage', 'grade', 'submitted_at']

admin.site.register(StudentAnswer)