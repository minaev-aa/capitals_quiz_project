"""Описание окон для записи"""

import re
import os
from django import forms
from django.conf import settings


# Проверка, что папка static/images существует
try:
    static_base_dir = (settings.STATICFILES_DIRS[0]
                       if settings.STATICFILES_DIRS
                       else os.path.join(settings.BASE_DIR, 'static'))
    IMAGE_UPLOAD_DIR = os.path.join(static_base_dir, 'images')
    os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)
except IndexError:
    print("Warning: STATICFILES_DIRS is not configured correctly in settings.py.")
    IMAGE_UPLOAD_DIR = os.path.join(settings.BASE_DIR, 'static', 'images')
    os.makedirs(IMAGE_UPLOAD_DIR, exist_ok=True)

class AddCountryForm(forms.Form):
    """Класс окна записи"""

    country = forms.CharField(
        label='Страна',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите страну'})
    )
    capital = forms.CharField(
        label='Столица',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите столицу'})
    )
    image = forms.FileField(
        label='Иллюстрация (опционально)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    def clean_country(self):
        """Форма записи страны и валидация на тип"""
        country = self.cleaned_data.get('country')
        if not country or not country.strip():
            raise forms.ValidationError("Название страны не может быть пустым.")
        if not re.fullmatch(r'[a-zA-Zа-яА-ЯёЁ\s-]+', country):
            raise forms.ValidationError("Название страны должно состоять только из букв.")
        return country.strip()

    def clean_capital(self):
        """Форма записи столицы и валидация на тип"""
        capital = self.cleaned_data.get('capital')
        if not capital or not capital.strip():
            raise forms.ValidationError("Название столицы не может быть пустым.")
        if not re.fullmatch(r'[a-zA-Zа-яА-ЯёЁ\s-]+', capital):
            raise forms.ValidationError("Название столицы должно состоять только из буквы.")
        return capital.strip()

    def clean_image(self):
        """Форма прикрепления изображения и валидация на тип"""
        image = self.cleaned_data.get('image')
        if image:
            allowed_extensions = ['.png', '.jpg', '.jpeg', '.gif']
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                     "Неподдерживаемый тип файла. "
                     "Используйте PNG, JPG, JPEG или GIF."
                )
        return image
