import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.spinner import Spinner
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.properties import NumericProperty, ListProperty
import os
import time

# Импортируем наши модули
from audio_processor import AudioProcessor
from rhythm_analyzer import RhythmAnalyzer

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
        device_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        device_layout.add_widget(Label(text='Устройство:', size_hint_x=0.3))
        
        self.device_spinner = Spinner(text='Выберите устройство', size_hint_x=0.7)
        self.device_spinner.bind(text=self.on_device_selected)
        device_layout.add_widget(self.device_spinner)
        
        self.add_widget(device_layout)
        
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
        self.update_device_list()
        
        # Обновление статистики
        Clock.schedule_interval(self.update_stats, 1.0)
    
    def update_device_list(self):
        """Обновление списка устройств ввода"""
        try:
            devices = self.audio_processor.get_input_devices()
            device_names = [f"{i}: {d['name']}" for i, d in enumerate(devices)]
            
            if device_names:
                self.device_spinner.values = device_names
                self.device_spinner.text = device_names[0]
            else:
                self.device_spinner.values = ['Нет доступных устройств']
                self.device_spinner.text = 'Нет доступных устройств'
        except Exception as e:
            self.status_label.text = f'Ошибка получения списка устройств: {str(e)}'
    
    def on_device_selected(self, instance, text):
        """Обработчик выбора устройства ввода"""
        if text.startswith('Нет доступных устройств'):
            return
        
        try:
            device_id = int(text.split(':')[0])
            self.audio_processor.set_device(device_id)
            self.status_label.text = f'Выбрано устройство: {text}'
        except Exception as e:
            self.status_label.text = f'Ошибка выбора устройства: {str(e)}'
    
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

class GuitarTrainerApp(App):
    def build(self):
        return MetronomeWidget()

if __name__ == '__main__':
    GuitarTrainerApp().run() 