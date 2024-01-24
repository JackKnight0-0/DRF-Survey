from django.urls import path

import survey.views as views

urlpatterns = [
    # survey
    path('', views.SurveyListAPIView.as_view()),
    path('my-survey/', views.ShowMySurveyAPIView.as_view()),
    path('new/', views.SurveyCreateAPIView.as_view()),
    path('statistic/<slug:slug>/', views.ShowStatisticOfSurvey.as_view(), name='survey_statistic'),
    path('edit/<slug:slug>/', views.SurveyUpdateAPIView.as_view()),
    path('published/<slug:slug>/', views.PublishedSurvey.as_view()),
    path('submit/<slug:slug>/', views.SurveySubmitAPIView.as_view()),
    path('delete/<slug:slug>/', views.SurveyDeleteAPIView.as_view()),
    # questions
    path('questions/create/<slug:survey_slug>/', views.QuestionCreateAPIView.as_view()),
    path('questions/delete/<int:pk>/', views.QuestionDeleteAPIView.as_view()),
    # answer
    path('answer-to-qestion/<int:question_id>/', views.AddAnswerToQuestionAPIView.as_view()),
    path('answer/delete/<int:pk>/', views.DeleteAnswerAPIView.as_view()),
    # greedy slug
    path('<slug:slug>/', views.SurveyDetailAPIView.as_view()),
]
