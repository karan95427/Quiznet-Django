from django.contrib import admin
from .models import Quiz, Question, UserResponse

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic', 'created_at')
    search_fields = ('topic',)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'question_type', 'difficulty')
    search_fields = ('question_text',)

@admin.register(UserResponse)
class UserResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'question', 'is_correct', 'topic', 'question_type', 'difficulty', 'answered_at')
    list_filter = ('is_correct', 'topic', 'question_type', 'difficulty')
    search_fields = ('user__username', 'question__question_text')
