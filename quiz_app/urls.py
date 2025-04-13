"""Сопоставляет URL-адреса с соответствующими функциями, которые должны обрабатывать эти запросы."""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'), # 1. Базовая страница
    path('list/', views.country_list, name='country_list'), # 2. Список стран
    path('add/', views.add_country, name='add_country'), # 3. Страница добавления
    path('quiz/', views.quiz_page, name='quiz_page'), # 4. Страница викторины
    path('quiz/process/', views.process_quiz, name='process_quiz'), # Обработка викторины
    path('leaders/', views.leaders_page, name='leaders_page'), # 5. Страница лидеров
]
