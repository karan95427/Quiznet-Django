from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# This class will become a table in your database for storing each quiz.
class Quiz(models.Model):
    topic = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This is just a helpful text representation of a Quiz object.
        return f"Quiz on {self.topic}({self.created_at.date()})"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    
    question_type = models.CharField(max_length=3,default='MCQ')
    question_text = models.TextField()
    options = models.JSONField(default=list,blank=True) 
    correct_answer = models.TextField(blank=True ,null=True, max_length=255)
    explanation = models.TextField(blank=True,null=True) # blank=True means this field is optional.
    difficulty=models.CharField(max_length=20,default="Medium")

    def __str__(self):
        return f"{self.question_type}: {self.question_text[:50]}..."
    
class UserResponse(models.Model):
    """
        Track how each user answered each question, plus metadata for adaptive learning.
        
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    user_answer = models.TextField()
    is_correct = models.BooleanField()
    timestamp = models.DateTimeField(auto_now_add=True)
    

    topic = models.CharField(max_length=200, blank=True, db_index=True)
    question_type = models.CharField(max_length=50, blank=True, db_index=True)
    difficulty = models.CharField(max_length=20, default='medium', blank=True, db_index=True)
    time_taken = models.FloatField(null=True, blank=True, help_text="Time taken in seconds")
    answered_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-answered_at']

    def save(self, *args, **kwargs):
        # keep topic/question_type/difficulty synced if they aren't set
        try:
            if self.question and (not self.topic):
                # pull topic from related quiz if available
                self.topic = self.question.quiz.topic
            if self.question and (not self.question_type):
                self.question_type = (self.question.question_type or "").upper()
            if self.question and (not self.difficulty):
                # use question.difficulty if you stored it, otherwise default 'medium'
                self.difficulty = getattr(self.question, 'difficulty', 'medium') or 'medium'
        except Exception:
            pass

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.question.id} - {'correct' if self.is_correct else 'wrong'}"