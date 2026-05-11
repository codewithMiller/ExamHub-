from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('manage/', views.manage_exams, name='manage_exams'),
    path('manage/create/', views.create_exam, name='create_exam'),
    path('manage/<int:exam_id>/questions/', views.add_question, name='add_question'),
    path('manage/<int:exam_id>/delete/', views.delete_exam, name='delete_exam'),
    path('exam/<int:exam_id>/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/leaderboard/', views.leaderboard, name='leaderboard'),
]