from django.urls import path
from .views import quiz_view, quiz_history_view, logout_view, registeruser, score_chart_view

app_name = 'aiquiz'

urlpatterns = [
    path("", quiz_view, name="quiz"),
    path("logout/", logout_view, name="logout"),
    path("history/", quiz_history_view, name="quiz_history"),
    path("score-chart/", score_chart_view, name="score_chart"),
]