import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse, RoundedRectangle
import os
import time
import numpy as np
import random
import math
import json

# Импортируем наш модуль
from audio_processor import AudioProcessor

# Определяем цветовую схему в рок-стиле
COLORS = {
    'dark': (0.1, 0.1, 0.12, 1),  # Темный фон
    'background': (0.15, 0.15, 0.18, 1),  # Фон элементов
    'primary': (0.9, 0.3, 0.1, 1),  # Огненно-оранжевый
    'secondary': (0.5, 0.1, 0.5, 1),  # Пурпурный
    'accent': (0.9, 0.1, 0.5, 1),  # Розовый
    'text': (0.9, 0.9, 0.9, 1),  # Белый текст
    'highlight': (1.0, 0.8, 0.0, 1)  # Желтый для выделения
}

class RockButton(Button):
    """Стилизованная кнопка в рок-стиле"""
    def __init__(self, **kwargs):
        super(RockButton, self).__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Прозрачный фон для кастомной отрисовки
        self.color = COLORS['text']  # Цвет текста
        self.border = (0, 0, 0, 0)
        
        # Обновляем canvas при изменении размера
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        
        # Инициализируем canvas
        with self.canvas.before:
            Color(*COLORS['primary'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
            
            # Добавляем эффект "шума" для текстуры
            for _ in range(10):
                x = random.randint(0, 100) / 100.0
                y = random.randint(0, 100) / 100.0
                size = random.randint(1, 3) / 100.0
                alpha = random.randint(1, 10) / 20.0
                Color(1, 1, 1, alpha)
                Rectangle(pos=(self.pos[0] + x * self.width, self.pos[1] + y * self.height), 
                          size=(size * self.width, size * self.height))
    
    def _update_canvas(self, instance, value):
        """Обновление canvas при изменении размера"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def on_press(self):
        """Эффект при нажатии"""
        with self.canvas.before:
            Color(*COLORS['secondary'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
    
    def on_release(self):
        """Эффект при отпускании"""
        with self.canvas.before:
            Color(*COLORS['primary'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[5])

class RockSlider(Slider):
    """Стилизованный слайдер в рок-стиле"""
    def __init__(self, **kwargs):
        super(RockSlider, self).__init__(**kwargs)
        self.cursor_size = (30, 30)
        
        # Обновляем canvas при изменении размера
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        
        # Инициализируем canvas
        with self.canvas.before:
            # Фон слайдера
            Color(*COLORS['background'])
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[5])
            
            # Активная часть слайдера
            Color(*COLORS['primary'])
            self.active_rect = RoundedRectangle(
                pos=self.pos, 
                size=(self.value_pos[0] - self.pos[0], self.height), 
                radius=[5]
            )
    
    def _update_canvas(self, instance, value):
        """Обновление canvas при изменении размера"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
        # Обновляем активную часть слайдера
        self.active_rect.pos = self.pos
        self.active_rect.size = (self.value_pos[0] - self.pos[0], self.height)
    
    def on_value(self, instance, value):
        """Обновление активной части при изменении значения"""
        if hasattr(self, 'active_rect'):
            self.active_rect.size = (self.value_pos[0] - self.pos[0], self.height)

class SignalLevelIndicator(BoxLayout):
    """Виджет для отображения уровня сигнала"""
    def __init__(self, **kwargs):
        super(SignalLevelIndicator, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 50
        
        # Заголовок
        self.add_widget(Label(
            text='Уровень сигнала',
            size_hint_y=None,
            height=20
        ))
        
        # Контейнер для индикатора
        self.indicator_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.indicator_container)
        
        # Индикатор уровня
        with self.indicator_container.canvas:
            Color(0.2, 0.2, 0.2, 1)
            self.background = Rectangle(pos=self.indicator_container.pos, 
                                       size=self.indicator_container.size)
            self.indicator_color = Color(0.0, 0.7, 0.0, 1)
            self.indicator = Rectangle(pos=self.indicator_container.pos, 
                                      size=(0, self.indicator_container.height))
        
        # Обновление позиции и размера при изменении размера виджета
        self.indicator_container.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, instance, value):
        """Обновление позиции и размера индикатора"""
        self.background.pos = instance.pos
        self.background.size = instance.size
        self.indicator.pos = instance.pos
        # Сохраняем только ширину, высота остается прежней
        self.indicator.size = (self.indicator.size[0], instance.height)
    
    def set_level(self, level):
        """Установка уровня сигнала (0.0 - 1.0)"""
        # Ограничиваем уровень от 0 до 1
        level = max(0.0, min(1.0, level))
        
        # Масштабируем для лучшей визуализации (логарифмическая шкала)
        if level > 0:
            scaled_level = 0.2 + 0.8 * (np.log10(1 + 9 * level))
        else:
            scaled_level = 0
        
        # Обновляем ширину индикатора
        self.indicator.size = (scaled_level * self.indicator_container.width, 
                              self.indicator_container.height)
        
        # Меняем цвет в зависимости от уровня
        if level < 0.3:
            # Зеленый для низкого уровня
            self.indicator_color.rgb = (0.0, 0.7, 0.0)
        elif level < 0.7:
            # Желтый для среднего уровня
            self.indicator_color.rgb = (0.7, 0.7, 0.0)
        else:
            # Красный для высокого уровня
            self.indicator_color.rgb = (0.7, 0.0, 0.0)

class GuitarMonitorWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(GuitarMonitorWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        # Заголовок
        self.add_widget(Label(
            text='🎸 Guitar Sound Monitor',
            font_size='24sp',
            size_hint_y=None,
            height=50
        ))
        
        # Индикатор уровня сигнала
        self.signal_indicator = SignalLevelIndicator()
        self.add_widget(self.signal_indicator)
        
        # Выбор устройства ввода
        input_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        input_device_layout.add_widget(Label(text='Вход:', size_hint_x=0.3))
        
        self.input_device_spinner = Spinner(text='Выберите устройство', size_hint_x=0.7)
        self.input_device_spinner.bind(text=self.on_input_device_selected)
        input_device_layout.add_widget(self.input_device_spinner)
        
        self.add_widget(input_device_layout)
        
        # Выбор канала ввода
        input_channel_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        input_channel_layout.add_widget(Label(text='Канал:', size_hint_x=0.3))
        
        self.input_channel_spinner = Spinner(text='Канал 1', size_hint_x=0.7)
        self.input_channel_spinner.bind(text=self.on_input_channel_selected)
        input_channel_layout.add_widget(self.input_channel_spinner)
        
        self.add_widget(input_channel_layout)
        
        # Выбор устройства вывода
        output_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        output_device_layout.add_widget(Label(text='Выход:', size_hint_x=0.3))
        
        self.output_device_spinner = Spinner(text='Выберите устройство', size_hint_x=0.7)
        self.output_device_spinner.bind(text=self.on_output_device_selected)
        output_device_layout.add_widget(self.output_device_spinner)
        
        self.add_widget(output_device_layout)
        
        # Размер буфера (для минимизации задержки)
        buffer_size_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        buffer_size_layout.add_widget(Label(text='Размер буфера:', size_hint_x=0.3))
        
        self.buffer_size_spinner = Spinner(
            text='128',
            values=['64', '128', '256', '512', '1024'],
            size_hint_x=0.7
        )
        self.buffer_size_spinner.bind(text=self.on_buffer_size_selected)
        buffer_size_layout.add_widget(self.buffer_size_spinner)
        
        self.add_widget(buffer_size_layout)
        
        # Режим низкой задержки
        low_latency_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        low_latency_layout.add_widget(Label(text='Низкая задержка:', size_hint_x=0.3))
        
        self.low_latency_switch = Switch(active=True, size_hint_x=0.2)
        self.low_latency_switch.bind(active=self.on_low_latency_toggle)
        low_latency_layout.add_widget(self.low_latency_switch)
        
        self.low_latency_label = Label(text='Вкл', size_hint_x=0.5)
        low_latency_layout.add_widget(self.low_latency_label)
        
        self.add_widget(low_latency_layout)
        
        # Мониторинг звука
        monitoring_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        monitoring_layout.add_widget(Label(text='Мониторинг:', size_hint_x=0.3))
        
        self.monitoring_switch = Switch(active=False, size_hint_x=0.2)
        self.monitoring_switch.bind(active=self.on_monitoring_toggle)
        monitoring_layout.add_widget(self.monitoring_switch)
        
        self.monitoring_label = Label(text='Выкл', size_hint_x=0.5)
        monitoring_layout.add_widget(self.monitoring_label)
        
        self.add_widget(monitoring_layout)
        
        # Громкость мониторинга
        volume_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        volume_layout.add_widget(Label(text='Громкость:', size_hint_x=0.3))
        
        self.volume_slider = Slider(min=0.0, max=1.0, value=1.0, size_hint_x=0.5)
        self.volume_slider.bind(value=self.on_volume_change)
        volume_layout.add_widget(self.volume_slider)
        
        self.volume_label = Label(text='100%', size_hint_x=0.2)
        volume_layout.add_widget(self.volume_label)
        
        self.add_widget(volume_layout)
        
        # Порог громкости
        threshold_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        threshold_layout.add_widget(Label(text='Порог:', size_hint_x=0.3))
        
        self.threshold_slider = Slider(min=0.01, max=0.5, value=0.1, size_hint_x=0.5)
        self.threshold_slider.bind(value=self.on_threshold_change)
        threshold_layout.add_widget(self.threshold_slider)
        
        self.threshold_label = Label(text='0.10', size_hint_x=0.2)
        threshold_layout.add_widget(self.threshold_label)
        
        self.add_widget(threshold_layout)
        
        # Кнопки управления
        controls_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        self.start_button = Button(text='Старт', size_hint_x=0.5)
        self.start_button.bind(on_press=self.toggle_monitor)
        controls_layout.add_widget(self.start_button)
        
        self.add_widget(controls_layout)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.status_label)
        
        # Инициализация обработчика аудио
        self.audio_processor = AudioProcessor(callback=self.on_audio_detected)
        
        # Обновление списка устройств
        self.update_device_lists()
        
        # Запускаем обработчик аудио для отображения уровня сигнала
        self.audio_processor.start()
        
        # Запускаем обновление уровня сигнала
        Clock.schedule_interval(self.update_signal_level, 0.05)
    
    def update_signal_level(self, dt):
        """Обновление уровня сигнала"""
        # Получаем текущий уровень сигнала от аудио процессора
        if hasattr(self.audio_processor, 'last_rms'):
            level = self.audio_processor.last_rms
            self.signal_indicator.set_level(level)
    
    def update_device_lists(self, *args):
        """Обновление списков устройств ввода/вывода"""
        try:
            # Получаем список устройств ввода
            self.input_devices = self.audio_processor.get_input_devices()
            
            if self.input_devices:
                # Заполняем выпадающий список устройств ввода
                device_names = [device['name'] for device in self.input_devices]
                self.input_device_spinner.values = device_names
                
                # Выбираем первое устройство по умолчанию
                if self.input_device_spinner.text == 'Выберите устройство':
                    self.input_device_spinner.text = device_names[0]
                    self.on_input_device_selected(self.input_device_spinner, device_names[0])
            else:
                self.status_label.text = 'Устройства ввода не найдены'
        except Exception as e:
            self.status_label.text = f'Ошибка получения устройств ввода: {str(e)}'
            
        try:
            # Получаем список устройств вывода
            self.output_devices = self.audio_processor.get_output_devices()
            
            if self.output_devices:
                # Заполняем выпадающий список устройств вывода
                device_names = [device['name'] for device in self.output_devices]
                self.output_device_spinner.values = device_names
                
                # Выбираем первое устройство по умолчанию
                if self.output_device_spinner.text == 'Выберите устройство':
                    self.output_device_spinner.text = device_names[0]
                    self.on_output_device_selected(self.output_device_spinner, device_names[0])
            else:
                self.status_label.text = 'Устройства вывода не найдены'
        except Exception as e:
            self.status_label.text = f'Ошибка получения устройств вывода: {str(e)}'
    
    def on_input_device_selected(self, spinner, text):
        """Обработчик выбора устройства ввода"""
        try:
            # Находим выбранное устройство
            selected_device = next((device for device in self.input_devices if device['name'] == text), None)
            
            if selected_device:
                # Получаем количество каналов
                num_channels = selected_device['maxInputChannels']
                print(f"Выбрано устройство: {text} с {num_channels} входными каналами")
                
                # Обновляем список каналов
                channel_values = [f'Канал {i+1}' for i in range(num_channels)]
                self.input_channel_spinner.values = channel_values
                
                # Выбираем первый канал по умолчанию
                if not self.input_channel_spinner.text in channel_values:
                    self.input_channel_spinner.text = channel_values[0]
                
                # Устанавливаем устройство ввода
                self.audio_processor.set_input_device(selected_device['index'])
                
                # Обновляем статус
                self.status_label.text = f'Выбрано устройство ввода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства ввода: {str(e)}'
    
    def on_output_device_selected(self, spinner, text):
        """Обработчик выбора устройства вывода"""
        try:
            # Находим выбранное устройство
            selected_device = next((device for device in self.output_devices if device['name'] == text), None)
            
            if selected_device:
                # Устанавливаем устройство вывода
                self.audio_processor.set_output_device(selected_device['index'])
                
                # Обновляем статус
                self.status_label.text = f'Выбрано устройство вывода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства вывода: {str(e)}'
    
    def on_input_channel_selected(self, spinner, text):
        """Обработчик выбора канала ввода"""
        try:
            # Извлекаем номер канала из текста (например, "Канал 1" -> 0)
            channel = int(text.split(' ')[1]) - 1
            
            # Устанавливаем канал ввода
            self.audio_processor.set_input_channel(channel)
            
            # Обновляем статус
            self.status_label.text = f'Выбран канал: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора канала: {str(e)}'
    
    def on_buffer_size_selected(self, spinner, text):
        """Обработчик выбора размера буфера"""
        try:
            # Преобразуем текст в число
            buffer_size = int(text)
            
            # Устанавливаем размер буфера
            self.audio_processor.set_buffer_size(buffer_size)
            
            # Обновляем статус
            self.status_label.text = f'Установлен размер буфера: {buffer_size}'
        except Exception as e:
            self.status_label.text = f'Ошибка установки размера буфера: {str(e)}'
    
    def on_low_latency_toggle(self, switch, value):
        """Обработчик переключения режима низкой задержки"""
        try:
            # Устанавливаем режим низкой задержки
            self.audio_processor.set_low_latency(value)
            
            # Обновляем текст
            self.low_latency_label.text = 'Вкл' if value else 'Выкл'
            
            # Обновляем статус
            self.status_label.text = f'Режим низкой задержки: {"включен" if value else "выключен"}'
        except Exception as e:
            self.status_label.text = f'Ошибка переключения режима: {str(e)}'
    
    def on_monitoring_toggle(self, switch, value):
        """Обработчик переключения мониторинга"""
        try:
            # Устанавливаем мониторинг
            self.audio_processor.set_monitoring(value)
            
            # Обновляем текст
            self.monitoring_label.text = 'Вкл' if value else 'Выкл'
            
            # Обновляем статус
            self.status_label.text = f'Мониторинг: {"включен" if value else "выключен"}'
        except Exception as e:
            self.status_label.text = f'Ошибка переключения мониторинга: {str(e)}'
    
    def on_volume_change(self, slider, value):
        """Обработчик изменения громкости"""
        try:
            # Устанавливаем громкость
            self.audio_processor.set_monitoring_volume(value)
            
            # Обновляем текст (в процентах)
            self.volume_label.text = f'{int(value * 100)}%'
        except Exception as e:
            self.status_label.text = f'Ошибка установки громкости: {str(e)}'
    
    def on_threshold_change(self, slider, value):
        """Обработчик изменения порога громкости"""
        try:
            # Устанавливаем порог
            self.audio_processor.set_threshold(value)
            
            # Обновляем текст (с двумя знаками после запятой)
            self.threshold_label.text = f'{value:.2f}'
        except Exception as e:
            self.status_label.text = f'Ошибка установки порога: {str(e)}'
    
    def toggle_monitor(self, instance):
        """Переключение мониторинга"""
        if self.audio_processor.is_running:
            # Останавливаем
            self.audio_processor.stop()
            self.start_button.text = 'Старт'
            self.status_label.text = 'Мониторинг остановлен'
        else:
            # Запускаем
            self.audio_processor.start()
            self.start_button.text = 'Стоп'
            self.status_label.text = 'Мониторинг запущен'
    
    def on_audio_detected(self, timestamp, rms_value):
        """Обработчик обнаружения звука"""
        # Обновляем статус
        self.status_label.text = f'Обнаружен звук: RMS={rms_value:.4f}'
        
        # Здесь можно добавить дополнительную обработку звука
        print(f"Обнаружен звук: RMS={rms_value:.4f}, время={timestamp:.2f}")

class SettingsPopup(Popup):
    """Всплывающее окно настроек"""
    def __init__(self, app_instance, **kwargs):
        super(SettingsPopup, self).__init__(**kwargs)
        self.app = app_instance
        self.title = 'НАСТРОЙКИ'
        self.size_hint = (0.9, 0.9)
        self.auto_dismiss = False
        
        # Основной контейнер
        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Контейнер с фоном
        content = BoxLayout(orientation='vertical', spacing=10)
        with content.canvas.before:
            Color(*COLORS['dark'])
            RoundedRectangle(pos=content.pos, size=content.size, radius=[10])
        
        # Заголовок
        title_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        
        settings_title = Label(
            text='НАСТРОЙКИ ЗВУКА',
            font_size='18sp',
            bold=True,
            color=COLORS['primary'],
            halign='center',
            valign='middle'
        )
        settings_title.bind(size=settings_title.setter('text_size'))
        title_box.add_widget(settings_title)
        
        content.add_widget(title_box)
        
        # Создаем скроллируемый контейнер для настроек
        scroll_view = ScrollView(do_scroll_x=False)
        settings_container = BoxLayout(orientation='vertical', spacing=10, padding=10, size_hint_y=None)
        settings_container.bind(minimum_height=settings_container.setter('height'))
        
        # Выбор устройства ввода
        input_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        input_device_layout.add_widget(Label(
            text='ВХОД:',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.3
        ))
        
        self.input_device_spinner = Spinner(
            text='Выберите устройство',
            size_hint_x=0.7,
            background_color=COLORS['background'],
            color=COLORS['text']
        )
        self.input_device_spinner.bind(text=self.on_input_device_selected)
        input_device_layout.add_widget(self.input_device_spinner)
        
        settings_container.add_widget(input_device_layout)
        
        # Выбор канала ввода
        input_channel_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        input_channel_layout.add_widget(Label(
            text='КАНАЛ:',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.3
        ))
        
        self.input_channel_spinner = Spinner(
            text='Канал 1',
            size_hint_x=0.7,
            background_color=COLORS['background'],
            color=COLORS['text']
        )
        self.input_channel_spinner.bind(text=self.on_input_channel_selected)
        input_channel_layout.add_widget(self.input_channel_spinner)
        
        settings_container.add_widget(input_channel_layout)
        
        # Выбор устройства вывода
        output_device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        output_device_layout.add_widget(Label(
            text='ВЫХОД:',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.3
        ))
        
        self.output_device_spinner = Spinner(
            text='Выберите устройство',
            size_hint_x=0.7,
            background_color=COLORS['background'],
            color=COLORS['text']
        )
        self.output_device_spinner.bind(text=self.on_output_device_selected)
        output_device_layout.add_widget(self.output_device_spinner)
        
        settings_container.add_widget(output_device_layout)
        
        # Размер буфера (для минимизации задержки)
        buffer_size_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        buffer_size_layout.add_widget(Label(
            text='БУФЕР:',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.3
        ))
        
        self.buffer_size_spinner = Spinner(
            text='128',
            values=['64', '128', '256', '512', '1024'],
            size_hint_x=0.7,
            background_color=COLORS['background'],
            color=COLORS['text']
        )
        self.buffer_size_spinner.bind(text=self.on_buffer_size_selected)
        buffer_size_layout.add_widget(self.buffer_size_spinner)
        
        settings_container.add_widget(buffer_size_layout)
        
        # Режим низкой задержки
        low_latency_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        low_latency_layout.add_widget(Label(
            text='НИЗКАЯ ЗАДЕРЖКА:',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_x=0.7
        ))
        
        self.low_latency_switch = Switch(active=True, size_hint_x=0.3)
        self.low_latency_switch.bind(active=self.on_low_latency_toggle)
        low_latency_layout.add_widget(self.low_latency_switch)
        
        settings_container.add_widget(low_latency_layout)
        
        # Информация о необходимости перезапуска мониторинга
        restart_info = Label(
            text='После изменения настроек необходимо\nперезапустить мониторинг',
            font_size='14sp',
            color=COLORS['secondary'],
            size_hint_y=None,
            height=60,
            halign='center'
        )
        restart_info.bind(size=restart_info.setter('text_size'))
        settings_container.add_widget(restart_info)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            font_size='14sp',
            color=COLORS['text'],
            size_hint_y=None,
            height=50,
            halign='center'
        )
        self.status_label.bind(size=self.status_label.setter('text_size'))
        settings_container.add_widget(self.status_label)
        
        scroll_view.add_widget(settings_container)
        content.add_widget(scroll_view)
        
        # Кнопки внизу
        buttons_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        # Кнопка сохранения
        save_btn = RockButton(
            text='СОХРАНИТЬ',
            size_hint_x=0.5,
            font_size='16sp',
            bold=True
        )
        save_btn.bind(on_press=self.save_settings)
        buttons_layout.add_widget(save_btn)
        
        # Кнопка закрытия
        close_btn = RockButton(
            text='ЗАКРЫТЬ',
            size_hint_x=0.5,
            font_size='16sp',
            bold=True
        )
        close_btn.bind(on_press=self.dismiss)
        buttons_layout.add_widget(close_btn)
        
        content.add_widget(buttons_layout)
        main_layout.add_widget(content)
        
        self.content = main_layout
        
        # Загружаем настройки
        self.load_settings()
        
        # Обновляем списки устройств
        self.update_device_lists()
    
    def update_device_lists(self):
        """Обновление списков устройств ввода/вывода"""
        try:
            # Получаем список устройств ввода
            self.input_devices = self.app.audio_processor.get_input_devices()
            
            if self.input_devices:
                # Заполняем выпадающий список устройств ввода
                device_names = [device['name'] for device in self.input_devices]
                self.input_device_spinner.values = device_names
                
                # Выбираем устройство из настроек или первое по умолчанию
                if self.app.settings.get('input_device') in device_names:
                    self.input_device_spinner.text = self.app.settings['input_device']
                elif self.input_device_spinner.text not in device_names:
                    self.input_device_spinner.text = device_names[0]
                    
                # Обновляем список каналов
                self.update_channel_list()
            else:
                self.status_label.text = 'Устройства ввода не найдены'
        except Exception as e:
            self.status_label.text = f'Ошибка получения устройств ввода: {str(e)}'
        
        try:
            # Получаем список устройств вывода
            self.output_devices = self.app.audio_processor.get_output_devices()
            
            if self.output_devices:
                # Заполняем выпадающий список устройств вывода
                device_names = [device['name'] for device in self.output_devices]
                self.output_device_spinner.values = device_names
                
                # Выбираем устройство из настроек или первое по умолчанию
                if self.app.settings.get('output_device') in device_names:
                    self.output_device_spinner.text = self.app.settings['output_device']
                elif self.output_device_spinner.text not in device_names:
                    self.output_device_spinner.text = device_names[0]
            else:
                self.status_label.text = 'Устройства вывода не найдены'
        except Exception as e:
            self.status_label.text = f'Ошибка получения устройств вывода: {str(e)}'
    
    def update_channel_list(self):
        """Обновление списка доступных каналов"""
        if not hasattr(self, 'input_device_spinner') or not self.input_device_spinner.text:
            return
        
        # Получаем выбранное устройство
        selected_device = None
        for device in self.input_devices:
            if device['name'] == self.input_device_spinner.text:
                selected_device = device
                break
        
        if not selected_device:
            return
        
        # Получаем количество каналов
        num_channels = selected_device.get('maxInputChannels', 1)
        
        # Обновляем список каналов
        channel_values = [f'Канал {i+1}' for i in range(num_channels)]
        self.input_channel_spinner.values = channel_values
        
        # Выбираем канал из настроек или первый по умолчанию
        saved_channel = self.app.settings.get('input_channel')
        if saved_channel is not None and f'Канал {saved_channel+1}' in channel_values:
            self.input_channel_spinner.text = f'Канал {saved_channel+1}'
        elif not self.input_channel_spinner.text in channel_values and channel_values:
            self.input_channel_spinner.text = channel_values[0]
    
    def on_input_device_selected(self, spinner, text):
        """Обработчик выбора устройства ввода"""
        try:
            # Находим выбранное устройство
            selected_device = next((device for device in self.input_devices if device['name'] == text), None)
            
            if selected_device:
                # Обновляем список каналов
                self.update_channel_list()
                
                # Обновляем статус
                self.status_label.text = f'Выбрано устройство ввода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства ввода: {str(e)}'
    
    def on_output_device_selected(self, spinner, text):
        """Обработчик выбора устройства вывода"""
        try:
            # Находим выбранное устройство
            selected_device = next((device for device in self.output_devices if device['name'] == text), None)
            
            if selected_device:
                # Обновляем статус
                self.status_label.text = f'Выбрано устройство вывода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства вывода: {str(e)}'
    
    def on_input_channel_selected(self, spinner, text):
        """Обработчик выбора канала ввода"""
        try:
            # Извлекаем номер канала из текста (например, "Канал 1" -> 0)
            channel = int(text.split(' ')[1]) - 1
            
            # Обновляем статус
            self.status_label.text = f'Выбран канал: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора канала: {str(e)}'
    
    def on_buffer_size_selected(self, spinner, text):
        """Обработчик выбора размера буфера"""
        try:
            # Преобразуем текст в число
            buffer_size = int(text)
            
            # Обновляем статус
            self.status_label.text = f'Установлен размер буфера: {buffer_size}'
        except Exception as e:
            self.status_label.text = f'Ошибка установки размера буфера: {str(e)}'
    
    def on_low_latency_toggle(self, switch, value):
        """Обработчик переключения режима низкой задержки"""
        try:
            # Обновляем статус
            self.status_label.text = f'Режим низкой задержки: {"включен" if value else "выключен"}'
        except Exception as e:
            self.status_label.text = f'Ошибка переключения режима: {str(e)}'
    
    def load_settings(self):
        """Загрузка настроек из приложения"""
        # Устанавливаем значения из настроек
        if 'buffer_size' in self.app.settings:
            self.buffer_size_spinner.text = str(self.app.settings['buffer_size'])
        
        if 'low_latency' in self.app.settings:
            self.low_latency_switch.active = self.app.settings['low_latency']
    
    def save_settings(self, instance):
        """Сохранение настроек"""
        try:
            # Получаем выбранное устройство ввода
            input_device = None
            for device in self.input_devices:
                if device['name'] == self.input_device_spinner.text:
                    input_device = device
                    break
            
            # Получаем выбранное устройство вывода
            output_device = None
            for device in self.output_devices:
                if device['name'] == self.output_device_spinner.text:
                    output_device = device
                    break
            
            # Получаем выбранный канал
            channel = int(self.input_channel_spinner.text.split(' ')[1]) - 1
            
            # Получаем размер буфера
            buffer_size = int(self.buffer_size_spinner.text)
            
            # Получаем режим низкой задержки
            low_latency = self.low_latency_switch.active
            
            # Сохраняем настройки в приложении
            self.app.settings.update({
                'input_device': self.input_device_spinner.text,
                'input_device_index': input_device['index'] if input_device else 0,
                'output_device': self.output_device_spinner.text,
                'output_device_index': output_device['index'] if output_device else 0,
                'input_channel': channel,
                'buffer_size': buffer_size,
                'low_latency': low_latency
            })
            
            # Применяем настройки
            self.app.apply_settings()
            
            # Сохраняем настройки в файл
            self.app.save_settings()
            
            # Обновляем статус
            self.status_label.text = 'Настройки сохранены'
        except Exception as e:
            self.status_label.text = f'Ошибка сохранения настроек: {str(e)}'

class GuitarTrainerApp(App):
    """Приложение для тренировки ритма на гитаре в рок-стиле"""
    def build(self):
        # Устанавливаем заголовок окна
        self.title = 'ROCK GUITAR RHYTHM TRAINER'
        
        # Загружаем настройки
        self.settings = self.load_settings()
        
        # Создаем основной контейнер
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Добавляем фоновое изображение
        with root.canvas.before:
            # Темный фон
            Color(0.1, 0.1, 0.12, 1)
            self.bg_rect = Rectangle(pos=root.pos, size=root.size)
            
            # Добавляем эффект "шума" для текстуры
            for _ in range(100):
                x = random.randint(0, 100) / 100.0 * root.width
                y = random.randint(0, 100) / 100.0 * root.height
                size = random.randint(1, 3)
                alpha = random.randint(1, 10) / 20.0
                Color(1, 1, 1, alpha)
                Rectangle(pos=(x, y), size=(size, size))
        
        # Обновляем размер фона при изменении размера окна
        root.bind(size=self._update_bg_rect, pos=self._update_bg_rect)
        
        # Заголовок приложения
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=80)
        
        # Логотип (можно заменить на изображение)
        logo_box = BoxLayout(size_hint_x=0.2)
        with logo_box.canvas:
            # Рисуем стилизованную гитару
            Color(*COLORS['primary'])
            Line(points=[20, 20, 60, 60, 20, 60, 60, 20], width=2)
            Ellipse(pos=(30, 30), size=(20, 20))
        header.add_widget(logo_box)
        
        # Заголовок
        title_label = Label(
            text='ROCK GUITAR RHYTHM TRAINER',
            font_size='28sp',
            bold=True,
            color=COLORS['primary'],
            size_hint_x=0.8
        )
        header.add_widget(title_label)
        
        root.add_widget(header)
        
        # Основной контент - только индикатор уровня сигнала
        content = BoxLayout(orientation='vertical', spacing=10)
        
        # Индикатор уровня сигнала
        self.signal_indicator = SignalLevelIndicator()
        content.add_widget(self.signal_indicator)
        
        # Добавляем скроллинг для контента
        scroll_view = ScrollView(do_scroll_x=False)
        scroll_view.add_widget(content)
        root.add_widget(scroll_view)
        
        # Нижняя панель с кнопками
        bottom_panel = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=10)
        
        # Кнопка настроек
        settings_btn = RockButton(
            text='НАСТРОЙКИ',
            size_hint_x=0.5,
            font_size='16sp',
            bold=True
        )
        settings_btn.bind(on_press=self.show_settings)
        bottom_panel.add_widget(settings_btn)
        
        # Кнопка мониторинга
        self.monitoring_btn = RockButton(
            text='МОНИТОРИНГ ВЫКЛ',
            size_hint_x=0.5,
            font_size='16sp',
            bold=True
        )
        self.monitoring_btn.bind(on_press=self.toggle_monitoring)
        bottom_panel.add_widget(self.monitoring_btn)
        
        root.add_widget(bottom_panel)
        
        # Инициализация аудио процессора
        self.audio_processor = AudioProcessor(callback=self.on_audio_detected)
        
        # Применяем настройки
        self.apply_settings()
        
        # Запускаем обработчик аудио
        self.audio_processor.start()
        
        # Запускаем обновление уровня сигнала
        Clock.schedule_interval(self.update_signal_level, 0.05)
        
        return root
    
    def _update_bg_rect(self, instance, value):
        """Обновление размера фонового прямоугольника"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = instance.pos
            self.bg_rect.size = instance.size
    
    def update_signal_level(self, dt):
        """Обновление уровня сигнала"""
        # Получаем текущий уровень сигнала от аудио процессора
        if hasattr(self.audio_processor, 'last_rms'):
            level = self.audio_processor.last_rms
            self.signal_indicator.set_level(level)
    
    def on_audio_detected(self, timestamp, amplitude):
        """Обработчик обнаружения звука с гитары"""
        pass
    
    def show_settings(self, instance):
        """Показать настройки"""
        settings_popup = SettingsPopup(self)
        settings_popup.open()
    
    def toggle_monitoring(self, instance):
        """Переключение мониторинга"""
        if self.audio_processor.is_monitoring:
            # Выключаем мониторинг
            self.audio_processor.toggle_monitoring()
            self.monitoring_btn.text = 'МОНИТОРИНГ ВЫКЛ'
        else:
            # Включаем мониторинг
            if self.audio_processor.toggle_monitoring():
                self.monitoring_btn.text = 'МОНИТОРИНГ ВКЛ'
            else:
                # Если не удалось включить мониторинг
                self.monitoring_btn.text = 'ОШИБКА МОНИТОРИНГА'
    
    def load_settings(self):
        """Загрузка настроек из файла"""
        settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        default_settings = {
            'input_device': '',
            'input_device_index': 0,
            'output_device': '',
            'output_device_index': 0,
            'input_channel': 0,
            'buffer_size': 128,
            'low_latency': True
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Объединяем с дефолтными настройками для обратной совместимости
                    return {**default_settings, **settings}
            else:
                return default_settings
        except Exception as e:
            print(f"Ошибка загрузки настроек: {str(e)}")
            return default_settings
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {str(e)}")
    
    def apply_settings(self):
        """Применение настроек к аудио процессору"""
        try:
            # Устанавливаем устройство ввода
            if 'input_device_index' in self.settings:
                self.audio_processor.set_input_device(self.settings['input_device_index'])
            
            # Устанавливаем устройство вывода
            if 'output_device_index' in self.settings:
                self.audio_processor.set_output_device(self.settings['output_device_index'])
            
            # Устанавливаем канал ввода
            if 'input_channel' in self.settings:
                self.audio_processor.set_input_channel(self.settings['input_channel'])
            
            # Устанавливаем размер буфера
            if 'buffer_size' in self.settings:
                was_monitoring = self.audio_processor.is_monitoring
                
                # Останавливаем аудиопроцессор
                self.audio_processor.stop()
                
                # Устанавливаем новый размер буфера
                self.audio_processor.block_size = self.settings['buffer_size']
                
                # Устанавливаем режим низкой задержки
                self.audio_processor.use_low_latency = self.settings.get('low_latency', True)
                
                # Перезапускаем аудиопроцессор
                self.audio_processor.start()
                
                # Мониторинг не восстанавливаем автоматически - пользователь должен включить его вручную
                if was_monitoring:
                    print("Мониторинг был включен. Пожалуйста, включите его снова после изменения настроек.")
        except Exception as e:
            print(f"Ошибка применения настроек: {str(e)}")

if __name__ == '__main__':
    GuitarTrainerApp().run() 