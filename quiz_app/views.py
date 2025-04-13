"""Модуль функций обработки заппросов"""

# Create your views here.
import os
import random
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest
from django.conf import settings
from .csv_utils import read_countries, write_country, read_leaders, write_leader
from .forms import AddCountryForm

def home_page(request):
    """Базовая страница"""
    return render(request, 'quiz_app/home.html')

def country_list(request):
    """Список стран"""
    countries = read_countries()
    return render(request, 'quiz_app/country_list.html', {'countries': countries})

def add_country(request):
    """Добавление страны"""
    if request.method == 'POST':
        form = AddCountryForm(request.POST, request.FILES)
        # Проверяем, валидна ли форма
        if form.is_valid():
            country = form.cleaned_data['country']
            capital = form.cleaned_data['capital']
            image = form.cleaned_data.get('image')
            image_path_for_csv = ''

            # Обработка изображения
            if image:
                try:
                    static_base_dir = (settings.STATICFILES_DIRS[0]
                                       if settings.STATICFILES_DIRS
                                       else None)

                    if static_base_dir:
                        static_dir = os.path.join(static_base_dir, 'images')
                        os.makedirs(static_dir, exist_ok=True)

                        filename = image.name.replace(' ', '_')
                        file_path = os.path.join(static_dir, filename)
                        with open(file_path, 'wb+') as destination:
                            for chunk in image.chunks():
                                destination.write(chunk)

                        image_path_for_csv = os.path.join('images', filename).replace('\\', '/')
                    else:
                        print("Warning: settings.STATICFILES_DIRS not work. Image not saved.")

                except (OSError, FileNotFoundError) as e:
                    print(f"File operation error: {e}")
                    image_path_for_csv = ''

            # Добавляем проверку дублирования страны
            existing_countries = read_countries()
            if any(c['country'].lower() == country.lower() for c in existing_countries):
                form.add_error('country', 'Такая страна уже существует.')
                return render(request, 'quiz_app/add_country.html', {'form': form})

            write_country(country, capital, image_path_for_csv)

            return redirect('country_list')

    else:
        form = AddCountryForm()

    return render(request, 'quiz_app/add_country.html', {'form': form})

def read_countries_dict():
    """Создание словаря всех стран"""
    countries = read_countries()
    return {c.get('country'): c for c in countries if c.get('country')}

def quiz_page(request):
    """Страница викторины"""
    countries = read_countries()

    if not countries:
        # Очистка, если стран нет
        request.session.pop('shown_countries', None)
        request.session.pop('current_score', None)
        request.session.pop('player_name', None)
        request.session.pop('current_country', None)
        request.session.pop('correct_capital', None)
        request.session.pop('quiz_completed_successfully', None)
        request.session.modified = True
        return render(
            request,
            'quiz_app/quiz_page.html',
            {'error': 'Нет доступных стран для викторины. Пожалуйста, добавьте их.'}
        )

    # Проверка на победу
    if request.session.get('quiz_completed_successfully'):
        total_score = request.session.get('current_score', 0)
        player_name = request.session.get('player_name', 'Не указано')

        # Очистка для следующей игры
        request.session.pop('quiz_completed_successfully', None)
        request.session.pop('current_score', None)
        request.session.pop('shown_countries', None)
        request.session.pop('player_name', None) # Also clear player name for new game
        request.session.pop('current_country', None) # Clear current country
        request.session.pop('correct_capital', None) # Clear correct capital
        request.session.modified = True

        return render(request, 'quiz_app/quiz_page.html', {
            'game_over': True,
            'message': f"Поздравляем, вы прошли викторину! Ваш итоговый счет: {total_score}.",
            'total_score': total_score,
            'player_name': player_name
        })

    # Проверка на повторы вопросов
    if request.session.get('current_country'):
        current_country_name = request.session['current_country']

        all_countries_data = read_countries_dict()
        random_country = all_countries_data.get(current_country_name)

        if not random_country:
            # Если страна удалилась из файла
            request.session.pop('current_country', None)
            request.session.pop('correct_capital', None)
            return redirect('quiz_page')

    else:
        # Выбор новой случайной страны
        if 'shown_countries' not in request.session:
            request.session['shown_countries'] = []
            request.session['current_score'] = 0
            request.session.pop('player_name', None)
            request.session.modified = True

        available_countries = [
               c for c in countries
               if c.get('country') not in request.session.get('shown_countries', [])
        ]
        if not available_countries:
            request.session['quiz_completed_successfully'] = True
            request.session.modified = True
            return redirect('quiz_page')

        random_country = random.choice(available_countries)

        request.session['current_country'] = random_country.get('country')
        request.session['correct_capital'] = random_country.get('capital')
        request.session.modified = True

    context = {
        'country': request.session.get('current_country'),
        'image_path': random_country.get('image_path') if random_country else None, 
        'player_name': request.session.get('player_name'),
        'current_score': request.session.get('current_score', 0),
        'total_countries': len(countries),
        'shown_count': len(request.session.get('shown_countries', [])),
        'message': request.session.pop('last_message', None), 
        'is_correct': request.session.pop('last_is_correct', None),
    }
    return render(request, 'quiz_app/quiz_page.html', context)



def process_quiz(request):
    """Обработка викторины"""
    if request.method == 'POST':
        user_answer = request.POST.get('capital_guess', '').strip()
        correct_capital = request.session.get('correct_capital')
        country_name = request.session.get('current_country')

        if not correct_capital or not country_name:
            return redirect('quiz_page')

        player_name_from_post = request.POST.get('player_name', '').strip()

        request.session['player_name'] = player_name_from_post
        request.session.modified = True

        if not user_answer:
            return HttpResponseBadRequest("Пожалуйста, введите ответ.")

        is_correct = (user_answer.lower() == correct_capital.lower())

        if is_correct:
            request.session['current_score'] = request.session.get('current_score', 0) + 1
            message = f"Правильно! Столица {country_name} - это {correct_capital}."
            # Update shown countries list ONLY after correct answer
            shown_countries_list = request.session.get('shown_countries', [])
            shown_countries_list.append(country_name)
            request.session['shown_countries'] = shown_countries_list
            request.session.modified = True

            write_leader(request.session['player_name'], request.session['current_score'])

            request.session.pop('current_country', None)
            request.session.pop('correct_capital', None)

        else:
            message = f"Неправильно. Столица {country_name} - это {correct_capital}."
            request.session['current_score'] = 0
            request.session['shown_countries'] = []
            request.session.pop('player_name', None)
            request.session.pop('current_country', None)
            request.session.pop('correct_capital', None)

        request.session['last_message'] = message
        request.session['last_is_correct'] = is_correct
        request.session.modified = True

        return redirect('quiz_page')

    return redirect('quiz_page')

def leaders_page(request):
    """Страница лидеров"""
    leaders = read_leaders()
    return render(request, 'quiz_app/leaders_page.html', {'leaders': leaders})
