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
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.properties import NumericProperty, ListProperty
import os
import time
import numpy as np

# Импортируем наши модули
from audio_processor import AudioProcessor
from rhythm_analyzer import RhythmAnalyzer

class SignalGraph(BoxLayout):
    """Виджет для отображения графика сигнала"""
    def __init__(self, **kwargs):
        super(SignalGraph, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 150
        
        # Заголовок
        self.add_widget(Label(text='Сигнал с гитары', size_hint_y=None, height=30))
        
        # Область для графика
        self.graph_area = BoxLayout(size_hint_y=None, height=120)
        self.add_widget(self.graph_area)
        
        # Буфер для хранения последних значений сигнала
        self.buffer_size = 200
        self.signal_buffer = np.zeros(self.buffer_size)
        
        # Обновление графика
        Clock.schedule_interval(self.update, 1/30)
    
    def add_sample(self, value):
        """Добавление нового значения в буфер"""
        # Сдвигаем буфер влево и добавляем новое значение в конец
        self.signal_buffer = np.roll(self.signal_buffer, -1)
        self.signal_buffer[-1] = value
    
    def update(self, dt):
        """Обновление графика"""
        self.graph_area.canvas.clear()
        
        # Рисуем фон
        with self.graph_area.canvas:
            Color(0.1, 0.1, 0.1, 1)
            Rectangle(pos=self.graph_area.pos, size=self.graph_area.size)
            
            # Рисуем горизонтальные линии сетки
            Color(0.3, 0.3, 0.3, 1)
            for i in range(1, 4):
                y = self.graph_area.pos[1] + (i * self.graph_area.height / 4)
                Line(points=[self.graph_area.pos[0], y, 
                             self.graph_area.pos[0] + self.graph_area.width, y], 
                     width=1)
            
            # Рисуем порог обнаружения звука
            Color(1, 0.5, 0, 1)  # Оранжевый
            threshold_y = self.graph_area.pos[1] + (self.graph_area.height * 0.1)  # 10% от высоты
            Line(points=[self.graph_area.pos[0], threshold_y, 
                         self.graph_area.pos[0] + self.graph_area.width, threshold_y], 
                 width=1, dash_length=5, dash_offset=3)
            
            # Рисуем график сигнала
            Color(0, 1, 0, 1)  # Зеленый
            points = []
            
            for i in range(self.buffer_size):
                x = self.graph_area.pos[0] + (i * self.graph_area.width / self.buffer_size)
                # Масштабируем значение сигнала (0-1) на высоту графика
                y = self.graph_area.pos[1] + (self.signal_buffer[i] * self.graph_area.height)
                points.extend([x, y])
            
            if len(points) >= 4:  # Минимум 2 точки для линии
                Line(points=points, width=1.5)

class SignalLevelIndicator(BoxLayout):
    """Виджет для отображения уровня сигнала"""
    def __init__(self, **kwargs):
        super(SignalLevelIndicator, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 50
        self.padding = [10, 5]
        
        # Метка
        self.add_widget(Label(text='Уровень:', size_hint_x=0.3))
        
        # Индикатор уровня
        self.level_bar = ProgressBar(max=1.0, value=0, size_hint_x=0.5)
        self.add_widget(self.level_bar)
        
        # Числовое значение
        self.level_label = Label(text='0.00', size_hint_x=0.2)
        self.add_widget(self.level_label)
        
        # Текущий уровень сигнала
        self.current_level = 0
        self.peak_level = 0
        self.decay_rate = 0.05  # Скорость затухания пикового значения
        
        # Обновление индикатора
        Clock.schedule_interval(self.update, 1/30)
    
    def set_level(self, level):
        """Установка уровня сигнала"""
        self.current_level = level
        
        # Обновляем пиковое значение
        if level > self.peak_level:
            self.peak_level = level
    
    def update(self, dt):
        """Обновление индикатора"""
        # Постепенное затухание пикового значения
        self.peak_level = max(self.current_level, self.peak_level - self.decay_rate)
        
        # Обновляем индикатор и метку
        self.level_bar.value = self.current_level
        self.level_label.text = f'{self.current_level:.2f}'
        
        # Изменяем цвет в зависимости от уровня
        if self.current_level > 0.8:
            self.level_bar.value_normalized = 1.0  # Перегрузка - красный
        elif self.current_level > 0.5:
            self.level_bar.value_normalized = 0.7  # Высокий уровень - желтый
        else:
            self.level_bar.value_normalized = 0.4  # Нормальный уровень - зеленый

class RhythmVisualizer(BoxLayout):
    """Виджет для визуализации ритма"""
    beat_color = ListProperty([0.5, 0.5, 0.5, 1])
    beat_size = NumericProperty(30)
    
    def __init__(self, **kwargs):
        super(RhythmVisualizer, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = 100
        self.beat_positions = []
        self.current_beat = 0
        
        # Обновление визуализации
        Clock.schedule_interval(self.update, 1/30)
    
    def set_beats(self, num_beats):
        """Установка количества ударов"""
        self.beat_positions = []
        for i in range(num_beats):
            self.beat_positions.append(i / num_beats)
    
    def update(self, dt):
        """Обновление визуализации"""
        self.canvas.clear()
        
        # Рисуем фон
        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            Rectangle(pos=self.pos, size=self.size)
        
        # Рисуем индикаторы ритма
        for i, pos in enumerate(self.beat_positions):
            x = self.pos[0] + pos * self.width
            y = self.pos[1] + self.height / 2
            
            with self.canvas:
                if i == self.current_beat:
                    Color(1, 0, 0, 1)  # Текущий удар - красный
                else:
                    Color(0.5, 0.5, 0.5, 1)  # Остальные - серые
                
                Ellipse(pos=(x - self.beat_size/2, y - self.beat_size/2), 
                        size=(self.beat_size, self.beat_size))
    
    def set_current_beat(self, beat_index):
        """Установка текущего удара"""
        self.current_beat = beat_index % len(self.beat_positions) if self.beat_positions else 0

class FeedbackIndicator(BoxLayout):
    """Виджет для отображения обратной связи"""
    feedback_color = ListProperty([0.5, 0.5, 0.5, 1])
    
    def __init__(self, **kwargs):
        super(FeedbackIndicator, self).__init__(**kwargs)
        self.size_hint_y = None
        self.height = 50
        
        # Обновление визуализации
        Clock.schedule_interval(self.update, 1/30)
    
    def set_feedback(self, is_accurate):
        """Установка обратной связи"""
        if is_accurate:
            self.feedback_color = [0, 1, 0, 1]  # Зеленый - точное попадание
        else:
            self.feedback_color = [1, 0, 0, 1]  # Красный - неточное попадание
        
        # Сбрасываем цвет через некоторое время
        Clock.schedule_once(self.reset_color, 0.5)
    
    def reset_color(self, dt):
        """Сброс цвета"""
        self.feedback_color = [0.5, 0.5, 0.5, 1]
    
    def update(self, dt):
        """Обновление визуализации"""
        self.canvas.clear()
        with self.canvas:
            Color(*self.feedback_color)
            Rectangle(pos=self.pos, size=self.size)

class MetronomeWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(MetronomeWidget, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 20
        self.spacing = 10
        
        # Заголовок
        self.add_widget(Label(
            text='🎸 Guitar Rhythm Trainer',
            font_size='24sp',
            size_hint_y=None,
            height=50
        ))
        
        # Визуализация ритма
        self.rhythm_visualizer = RhythmVisualizer()
        self.rhythm_visualizer.set_beats(4)  # 4 удара в такте по умолчанию
        self.add_widget(self.rhythm_visualizer)
        
        # Индикатор обратной связи
        self.feedback_indicator = FeedbackIndicator()
        self.add_widget(self.feedback_indicator)
        
        # График сигнала
        self.signal_graph = SignalGraph()
        self.add_widget(self.signal_graph)
        
        # Индикатор уровня сигнала
        self.signal_indicator = SignalLevelIndicator()
        self.add_widget(self.signal_indicator)
        
        # Контроль темпа
        tempo_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        tempo_layout.add_widget(Label(text='Темп (BPM):', size_hint_x=0.3))
        
        self.tempo_slider = Slider(min=40, max=220, value=80, size_hint_x=0.5)
        self.tempo_slider.bind(value=self.on_tempo_change)
        tempo_layout.add_widget(self.tempo_slider)
        
        self.tempo_label = Label(text='80', size_hint_x=0.2)
        tempo_layout.add_widget(self.tempo_label)
        
        self.add_widget(tempo_layout)
        
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
        self.start_button.bind(on_press=self.toggle_trainer)
        controls_layout.add_widget(self.start_button)
        
        self.add_widget(controls_layout)
        
        # Статистика
        self.stats_label = Label(
            text='Точность: 0%',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.stats_label)
        
        # Статус
        self.status_label = Label(
            text='Готов к работе',
            size_hint_y=None,
            height=30
        )
        self.add_widget(self.status_label)
        
        # Инициализация метронома
        self.is_playing = False
        self.tempo = 80  # BPM
        self.beat_event = None
        
        # Загрузка звука метронома
        self.click_sound = None
        try:
            # Попробуем использовать встроенный звук
            sound_file = os.path.join(os.path.dirname(__file__), 'click.wav')
            if os.path.exists(sound_file):
                self.click_sound = SoundLoader.load(sound_file)
            else:
                self.status_label.text = 'Звук метронома не найден'
        except Exception as e:
            self.status_label.text = f'Ошибка загрузки звука: {str(e)}'
        
        # Инициализация обработчика аудио и анализатора ритма
        self.audio_processor = AudioProcessor(callback=self.on_audio_detected)
        self.rhythm_analyzer = RhythmAnalyzer(tolerance=0.1)
        
        # Обновление списка устройств
        self.update_device_lists()
        
        # Обновление статистики
        Clock.schedule_interval(self.update_stats, 1.0)
        
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
            self.signal_graph.add_sample(level)
    
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
                if not self.input_device_spinner.text or self.input_device_spinner.text not in device_names:
                    self.input_device_spinner.text = device_names[0]
                    # Устанавливаем устройство
                    self.audio_processor.set_device(self.input_devices[0]['index'])
                    # Обновляем список каналов
                    self.update_channel_list()
            else:
                self.input_device_spinner.values = ['Нет доступных устройств']
                self.input_device_spinner.text = 'Нет доступных устройств'
        except Exception as e:
            self.status_label.text = f'Ошибка получения списка устройств ввода: {str(e)}'
        
        try:
            # Получаем список устройств вывода
            self.output_devices = self.audio_processor.get_output_devices()
            
            if self.output_devices:
                # Заполняем выпадающий список устройств вывода
                device_names = [device['name'] for device in self.output_devices]
                self.output_device_spinner.values = device_names
                
                # Выбираем первое устройство по умолчанию
                if not self.output_device_spinner.text or self.output_device_spinner.text not in device_names:
                    self.output_device_spinner.text = device_names[0]
                    # Устанавливаем устройство вывода
                    self.audio_processor.set_output_device(self.output_devices[0]['index'])
            else:
                self.output_device_spinner.values = ['Нет доступных устройств']
                self.output_device_spinner.text = 'Нет доступных устройств'
        except Exception as e:
            self.status_label.text = f'Ошибка получения списка устройств вывода: {str(e)}'
    
    def update_channel_list(self, *args):
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
        device_id = selected_device['index']
        channels = self.audio_processor.get_device_channels(device_id)
        
        # Обновляем список каналов
        channel_values = [str(i) for i in range(channels)]
        self.input_channel_spinner.values = channel_values
        
        # Если текущий выбранный канал больше доступных, сбрасываем на первый
        if not self.input_channel_spinner.text or int(self.input_channel_spinner.text) >= channels:
            self.input_channel_spinner.text = "0" if channel_values else ""
        
        print(f"Обновлен список каналов для устройства {selected_device['name']}: {channel_values}")
    
    def on_input_device_selected(self, instance, text):
        """Обработчик выбора устройства ввода"""
        try:
            # Находим выбранное устройство
            selected_device = None
            for device in self.input_devices:
                if device['name'] == text:
                    selected_device = device
                    break
            
            if selected_device:
                # Устанавливаем устройство
                self.audio_processor.set_device(selected_device['index'])
                
                # Обновляем список каналов
                self.update_channel_list()
                
                self.status_label.text = f'Выбрано устройство ввода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства ввода: {str(e)}'
    
    def on_input_channel_selected(self, instance, text):
        """Обработчик выбора входного канала"""
        try:
            channel = int(text)
            if self.audio_processor.set_input_channel(channel):
                self.status_label.text = f'Выбран входной канал: {channel}'
            else:
                self.status_label.text = f'Ошибка выбора канала: канал {channel} недоступен'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора входного канала: {str(e)}'
    
    def on_output_device_selected(self, instance, text):
        """Обработчик выбора устройства вывода"""
        try:
            # Находим выбранное устройство
            selected_device = None
            for device in self.output_devices:
                if device['name'] == text:
                    selected_device = device
                    break
            
            if selected_device:
                # Устанавливаем устройство вывода
                self.audio_processor.set_output_device(selected_device['index'])
                self.status_label.text = f'Выбрано устройство вывода: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства вывода: {str(e)}'
    
    def on_monitoring_toggle(self, instance, value):
        """Обработчик переключения мониторинга"""
        if value:
            # Включаем мониторинг
            if self.audio_processor.toggle_monitoring():
                self.monitoring_label.text = 'Вкл'
                self.status_label.text = 'Мониторинг включен'
            else:
                self.monitoring_switch.active = False
                self.monitoring_label.text = 'Выкл'
                self.status_label.text = 'Ошибка включения мониторинга'
        else:
            # Выключаем мониторинг
            self.audio_processor.toggle_monitoring()
            self.monitoring_label.text = 'Выкл'
            self.status_label.text = 'Мониторинг выключен'
    
    def on_tempo_change(self, instance, value):
        """Обработчик изменения темпа"""
        self.tempo = int(value)
        self.tempo_label.text = str(self.tempo)
        
        # Обновляем темп в анализаторе ритма
        self.rhythm_analyzer.set_tempo(self.tempo)
        
        # Если метроном играет, обновляем интервал
        if self.is_playing:
            self.stop_metronome()
            self.start_metronome()
    
    def on_threshold_change(self, instance, value):
        """Обработчик изменения порога громкости"""
        threshold = round(value, 2)
        self.threshold_label.text = f'{threshold:.2f}'
        self.audio_processor.set_threshold(threshold)
    
    def toggle_trainer(self, instance):
        """Переключение состояния тренажера"""
        if self.is_playing:
            self.stop_trainer()
            self.start_button.text = 'Старт'
        else:
            self.start_trainer()
            self.start_button.text = 'Стоп'
    
    def start_trainer(self):
        """Запуск тренажера"""
        self.is_playing = True
        
        # Запускаем метроном
        self.start_metronome()
        
        # Запускаем анализатор ритма
        self.rhythm_analyzer.start()
        
        # Запускаем обработчик аудио
        self.audio_processor.start()
        
        self.status_label.text = f'Тренажер запущен: {self.tempo} BPM'
    
    def stop_trainer(self):
        """Остановка тренажера"""
        self.is_playing = False
        
        # Останавливаем метроном
        self.stop_metronome()
        
        # Останавливаем анализатор ритма
        self.rhythm_analyzer.stop()
        
        # Останавливаем обработчик аудио
        self.audio_processor.stop()
        
        self.status_label.text = 'Тренажер остановлен'
    
    def start_metronome(self):
        """Запуск метронома"""
        interval = 60.0 / self.tempo  # Интервал в секундах между ударами
        self.beat_event = Clock.schedule_interval(self.beat, interval)
    
    def stop_metronome(self):
        """Остановка метронома"""
        if self.beat_event:
            self.beat_event.cancel()
    
    def beat(self, dt):
        """Обработчик удара метронома"""
        # Визуальная индикация
        current_beat = (self.rhythm_visualizer.current_beat + 1) % 4
        self.rhythm_visualizer.set_current_beat(current_beat)
        
        # Звуковая индикация
        if self.click_sound:
            self.click_sound.play()
    
    def on_audio_detected(self, timestamp, amplitude):
        """Обработчик обнаружения звука с гитары"""
        if not self.is_playing:
            return
        
        # Анализируем попадание в ритм
        is_accurate, deviation = self.rhythm_analyzer.analyze_hit(timestamp)
        
        # Обновляем индикатор обратной связи
        self.feedback_indicator.set_feedback(is_accurate)
    
    def update_stats(self, dt):
        """Обновление статистики"""
        if not self.is_playing:
            return
        
        stats = self.rhythm_analyzer.get_stats()
        accuracy = stats['accuracy'] * 100
        
        self.stats_label.text = f"Точность: {accuracy:.1f}% ({stats['accurate_hits']}/{stats['total_hits']})"
    
    def on_volume_change(self, instance, value):
        """Обработчик изменения громкости мониторинга"""
        volume = round(value, 2)
        self.volume_label.text = f'{int(volume * 100)}%'
        
        # Устанавливаем громкость мониторинга
        if hasattr(self.audio_processor, 'set_monitoring_volume'):
            self.audio_processor.set_monitoring_volume(volume)

class GuitarTrainerApp(App):
    def build(self):
        return MetronomeWidget()

if __name__ == '__main__':
    GuitarTrainerApp().run() 