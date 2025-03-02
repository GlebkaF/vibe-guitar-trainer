import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import os
import time
import numpy as np

# Импортируем наш модуль
from audio_processor import AudioProcessor

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

class GuitarMonitorApp(App):
    def build(self):
        return GuitarMonitorWidget()

if __name__ == '__main__':
    GuitarMonitorApp().run() 