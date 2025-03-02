import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import time

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем Kivy, чтобы избежать ошибок импорта
sys.modules['kivy'] = MagicMock()
sys.modules['kivy.app'] = MagicMock()
sys.modules['kivy.uix.boxlayout'] = MagicMock()
sys.modules['kivy.uix.button'] = MagicMock()
sys.modules['kivy.uix.label'] = MagicMock()
sys.modules['kivy.uix.slider'] = MagicMock()
sys.modules['kivy.uix.spinner'] = MagicMock()
sys.modules['kivy.uix.switch'] = MagicMock()
sys.modules['kivy.uix.progressbar'] = MagicMock()
sys.modules['kivy.uix.popup'] = MagicMock()
sys.modules['kivy.uix.scrollview'] = MagicMock()
sys.modules['kivy.uix.floatlayout'] = MagicMock()
sys.modules['kivy.uix.relativelayout'] = MagicMock()
sys.modules['kivy.uix.widget'] = MagicMock()
sys.modules['kivy.clock'] = MagicMock()
sys.modules['kivy.graphics'] = MagicMock()
sys.modules['kivy.core.audio'] = MagicMock()

# Теперь импортируем модули из main.py
from main import RhythmTrainerWidget, GuitarTrainerApp

class TestRhythmTrainer(unittest.TestCase):
    """Тесты для компонентов ритм-тренера."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем мок для Clock
        self.clock_patcher = patch('kivy.clock.Clock')
        self.mock_clock = self.clock_patcher.start()
        
        # Создаем мок для SoundLoader
        self.sound_loader_patcher = patch('kivy.core.audio.SoundLoader')
        self.mock_sound_loader = self.sound_loader_patcher.start()
        
        # Создаем мок для звуков
        self.mock_sound = MagicMock()
        self.mock_sound_loader.load.return_value = self.mock_sound
        
        # Создаем мок для AudioProcessor
        self.audio_processor_patcher = patch('audio_processor.AudioProcessor')
        self.mock_audio_processor = self.audio_processor_patcher.start()
        
        # Создаем экземпляр RhythmTrainerWidget
        self.rhythm_trainer = RhythmTrainerWidget()
        
        # Мокаем методы, которые взаимодействуют с GUI
        self.rhythm_trainer.draw_notes = MagicMock()
        self.rhythm_trainer.flash_line = MagicMock()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        self.clock_patcher.stop()
        self.sound_loader_patcher.stop()
        self.audio_processor_patcher.stop()
    
    def test_toggle_training(self):
        """Тест переключения режима тренировки."""
        # Изначально тренировка не активна
        self.assertFalse(self.rhythm_trainer.is_training)
        
        # Включаем тренировку
        self.rhythm_trainer.toggle_training()
        self.assertTrue(self.rhythm_trainer.is_training)
        
        # Выключаем тренировку
        self.rhythm_trainer.toggle_training()
        self.assertFalse(self.rhythm_trainer.is_training)
    
    def test_start_training(self):
        """Тест запуска тренировки."""
        # Запускаем тренировку
        self.rhythm_trainer.start_training()
        
        # Проверяем, что тренировка активна
        self.assertTrue(self.rhythm_trainer.is_training)
        
        # Проверяем, что были запланированы события
        self.mock_clock.schedule_interval.assert_called()
        self.mock_clock.schedule_once.assert_called()
    
    def test_stop_training(self):
        """Тест остановки тренировки."""
        # Сначала запускаем тренировку
        self.rhythm_trainer.start_training()
        
        # Останавливаем тренировку
        self.rhythm_trainer.stop_training()
        
        # Проверяем, что тренировка не активна
        self.assertFalse(self.rhythm_trainer.is_training)
        
        # Проверяем, что события были отменены
        self.mock_clock.unschedule.assert_called()
    
    def test_on_audio_detected(self):
        """Тест обработки обнаруженного звука."""
        # Устанавливаем режим тренировки
        self.rhythm_trainer.is_training = True
        
        # Вызываем обработчик обнаруженного звука
        timestamp = time.time()
        amplitude = 0.8
        self.rhythm_trainer.on_audio_detected(timestamp, amplitude)
        
        # Проверяем, что была вызвана функция обработки звука
        # и что была вызвана функция flash_line
        self.rhythm_trainer.flash_line.assert_called_once()
    
    def test_generate_note(self):
        """Тест генерации ноты."""
        # Устанавливаем режим тренировки
        self.rhythm_trainer.is_training = True
        
        # Вызываем функцию генерации ноты
        self.rhythm_trainer.generate_note(0)
        
        # Проверяем, что была добавлена нота
        self.assertGreater(len(self.rhythm_trainer.notes), 0)
        
        # Проверяем, что была вызвана функция отрисовки нот
        self.rhythm_trainer.draw_notes.assert_called_once()
        
        # Проверяем, что была запланирована следующая нота
        self.mock_clock.schedule_once.assert_called()

class TestGuitarTrainerApp(unittest.TestCase):
    """Тесты для основного приложения GuitarTrainerApp."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем мок для AudioProcessor
        self.audio_processor_patcher = patch('audio_processor.AudioProcessor')
        self.mock_audio_processor_class = self.audio_processor_patcher.start()
        
        # Создаем мок для экземпляра AudioProcessor
        self.mock_audio_processor = MagicMock()
        self.mock_audio_processor_class.return_value = self.mock_audio_processor
        
        # Создаем мок для json
        self.json_patcher = patch('json.load')
        self.mock_json_load = self.json_patcher.start()
        self.mock_json_load.return_value = {
            'input_device': 0,
            'output_device': 0,
            'input_channel': 0,
            'buffer_size': 1024,
            'low_latency': True,
            'threshold': 0.2,
            'monitoring': False,
            'volume': 0.5,
            'bpm': 60,
            'speed': 1.0,
            'metronome_sound': True,
            'hit_sound': True
        }
        
        # Создаем мок для open
        self.open_patcher = patch('builtins.open', create=True)
        self.mock_open = self.open_patcher.start()
        
        # Создаем экземпляр приложения
        self.app = GuitarTrainerApp()
        
        # Мокаем методы, которые взаимодействуют с GUI
        self.app.root = MagicMock()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        self.audio_processor_patcher.stop()
        self.json_patcher.stop()
        self.open_patcher.stop()
    
    def test_load_settings(self):
        """Тест загрузки настроек."""
        # Вызываем функцию загрузки настроек
        self.app.load_settings()
        
        # Проверяем, что были загружены настройки
        self.mock_json_load.assert_called_once()
        
        # Проверяем, что настройки были применены
        self.assertEqual(self.app.settings['bpm'], 60)
        self.assertEqual(self.app.settings['speed'], 1.0)
        self.assertEqual(self.app.settings['threshold'], 0.2)
        self.assertTrue(self.app.settings['metronome_sound'])
        self.assertTrue(self.app.settings['hit_sound'])
    
    def test_on_audio_detected(self):
        """Тест обработки обнаруженного звука."""
        # Создаем мок для rhythm_trainer
        self.app.rhythm_trainer = MagicMock()
        
        # Вызываем обработчик обнаруженного звука
        timestamp = time.time()
        amplitude = 0.8
        self.app.on_audio_detected(timestamp, amplitude)
        
        # Проверяем, что была вызвана функция обработки звука в rhythm_trainer
        self.app.rhythm_trainer.on_audio_detected.assert_called_once_with(timestamp, amplitude)
    
    def test_toggle_monitoring(self):
        """Тест переключения мониторинга."""
        # Вызываем функцию переключения мониторинга
        self.app.toggle_monitoring(None)
        
        # Проверяем, что была вызвана функция toggle_monitoring в audio_processor
        self.mock_audio_processor.toggle_monitoring.assert_called_once()

if __name__ == '__main__':
    unittest.main() 