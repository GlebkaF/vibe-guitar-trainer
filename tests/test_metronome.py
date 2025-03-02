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
from main import ControlPanel, RhythmTrainerWidget

class TestMetronome(unittest.TestCase):
    """Тесты для функциональности метронома."""
    
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
        
        # Создаем экземпляр RhythmTrainerWidget
        self.rhythm_trainer = RhythmTrainerWidget()
        
        # Создаем мок для приложения
        self.mock_app = MagicMock()
        
        # Создаем экземпляр ControlPanel
        self.control_panel = ControlPanel(self.rhythm_trainer, self.mock_app)
        
        # Мокаем методы, которые взаимодействуют с GUI
        self.rhythm_trainer.draw_notes = MagicMock()
        self.rhythm_trainer.flash_line = MagicMock()
    
    def tearDown(self):
        """Очистка после каждого теста."""
        self.clock_patcher.stop()
        self.sound_loader_patcher.stop()
    
    def test_bpm_change(self):
        """Тест изменения BPM (ударов в минуту)."""
        # Создаем мок для слайдера
        mock_slider = MagicMock()
        mock_slider.value = 120
        
        # Вызываем обработчик изменения BPM
        self.control_panel.on_bpm_change(mock_slider, 120)
        
        # Проверяем, что BPM был изменен
        self.assertEqual(self.control_panel.bpm, 120)
        
        # Проверяем, что значение было передано в rhythm_trainer
        self.assertEqual(self.rhythm_trainer.bpm, 120)
        
        # Проверяем, что был обновлен интервал между нотами
        self.assertAlmostEqual(self.rhythm_trainer.note_interval, 60 / 120)
    
    def test_speed_change(self):
        """Тест изменения скорости движения нот."""
        # Создаем мок для слайдера
        mock_slider = MagicMock()
        mock_slider.value = 2.0
        
        # Вызываем обработчик изменения скорости
        self.control_panel.on_speed_change(mock_slider, 2.0)
        
        # Проверяем, что скорость была изменена
        self.assertEqual(self.control_panel.speed, 2.0)
        
        # Проверяем, что значение было передано в rhythm_trainer
        self.assertEqual(self.rhythm_trainer.speed, 2.0)
    
    def test_metronome_sound_toggle(self):
        """Тест переключения звука метронома."""
        # Создаем мок для переключателя
        mock_switch = MagicMock()
        
        # Включаем звук метронома
        mock_switch.active = True
        self.control_panel.on_metronome_sound_toggle(mock_switch, True)
        
        # Проверяем, что звук метронома включен
        self.assertTrue(self.rhythm_trainer.play_metronome_sound)
        
        # Выключаем звук метронома
        mock_switch.active = False
        self.control_panel.on_metronome_sound_toggle(mock_switch, False)
        
        # Проверяем, что звук метронома выключен
        self.assertFalse(self.rhythm_trainer.play_metronome_sound)
    
    def test_hit_sound_toggle(self):
        """Тест переключения звука удара."""
        # Создаем мок для переключателя
        mock_switch = MagicMock()
        
        # Включаем звук удара
        mock_switch.active = True
        self.control_panel.on_hit_sound_toggle(mock_switch, True)
        
        # Проверяем, что звук удара включен
        self.assertTrue(self.rhythm_trainer.play_hit_sound)
        
        # Выключаем звук удара
        mock_switch.active = False
        self.control_panel.on_hit_sound_toggle(mock_switch, False)
        
        # Проверяем, что звук удара выключен
        self.assertFalse(self.rhythm_trainer.play_hit_sound)
    
    def test_sound_volume_change(self):
        """Тест изменения громкости звука."""
        # Создаем мок для слайдера
        mock_slider = MagicMock()
        mock_slider.value = 0.8
        
        # Вызываем обработчик изменения громкости
        self.control_panel.on_sound_volume_change(mock_slider, 0.8)
        
        # Проверяем, что громкость была изменена
        self.assertEqual(self.control_panel.sound_volume, 0.8)
        
        # Проверяем, что значение было передано в rhythm_trainer
        self.assertEqual(self.rhythm_trainer.sound_volume, 0.8)
        
        # Проверяем, что громкость звуков была изменена
        if hasattr(self.rhythm_trainer, 'metronome_sound'):
            self.assertEqual(self.rhythm_trainer.metronome_sound.volume, 0.8)
        if hasattr(self.rhythm_trainer, 'hit_sound'):
            self.assertEqual(self.rhythm_trainer.hit_sound.volume, 0.8)

if __name__ == '__main__':
    unittest.main() 