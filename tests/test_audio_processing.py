import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os
import time
import queue

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio_processor import AudioProcessor

class TestAudioProcessing(unittest.TestCase):
    """Тесты для функциональности обработки аудио."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем мок для PyAudio
        self.pyaudio_patcher = patch('audio_processor.pyaudio.PyAudio')
        self.mock_pyaudio = self.pyaudio_patcher.start()
        
        # Настраиваем мок для PyAudio
        self.mock_pyaudio_instance = self.mock_pyaudio.return_value
        
        # Мок для устройств
        device_info = {'name': 'Test Device', 'maxInputChannels': 2, 'index': 0}
        self.mock_pyaudio_instance.get_default_input_device_info.return_value = device_info
        
        # Создаем экземпляр AudioProcessor с моком для callback
        self.mock_callback = MagicMock()
        self.audio_processor = AudioProcessor(callback=self.mock_callback, threshold=0.2)
        
        # Мок для аудио-потока
        self.mock_stream = MagicMock()
        self.mock_pyaudio_instance.open.return_value = self.mock_stream
    
    def tearDown(self):
        """Очистка после каждого теста."""
        self.pyaudio_patcher.stop()
        
        # Останавливаем аудио-процессор, если он запущен
        if self.audio_processor.is_running:
            self.audio_processor.stop()
    
    def test_audio_callback(self):
        """Тест callback-функции для обработки аудио."""
        # Создаем тестовые аудио-данные
        audio_data = np.zeros(1024, dtype=np.int16)
        audio_data[0:100] = 32767  # Максимальное значение для int16
        
        # Преобразуем в байты (как это делает PyAudio)
        audio_bytes = audio_data.tobytes()
        
        # Патчим метод queue.Queue.put, чтобы проверить, что данные добавляются в очередь
        with patch.object(self.audio_processor.audio_queue, 'put') as mock_put:
            # Вызываем callback-функцию
            result = self.audio_processor.audio_callback(audio_bytes, 1024, None, 0)
            
            # Проверяем, что метод put был вызван
            mock_put.assert_called_once()
            
            # Проверяем, что функция вернула правильное значение (продолжать захват)
            self.assertEqual(result, (None, 0))
    
    def test_set_monitoring(self):
        """Тест установки мониторинга."""
        # Проверяем, что мониторинг изначально выключен
        self.assertFalse(self.audio_processor.is_monitoring)
        
        # Патчим метод start_monitoring, чтобы избежать реальных вызовов
        with patch.object(self.audio_processor, 'start_monitoring'):
            # Включаем мониторинг
            self.audio_processor.set_monitoring(True)
            
            # Проверяем, что мониторинг включен
            self.assertTrue(self.audio_processor.is_monitoring)
        
        # Патчим метод stop_monitoring, чтобы избежать реальных вызовов
        with patch.object(self.audio_processor, 'stop_monitoring'):
            # Выключаем мониторинг
            self.audio_processor.set_monitoring(False)
            
            # Проверяем, что мониторинг выключен
            self.assertFalse(self.audio_processor.is_monitoring)
    
    def test_toggle_monitoring(self):
        """Тест переключения мониторинга."""
        # Проверяем, что мониторинг изначально выключен
        self.assertFalse(self.audio_processor.is_monitoring)
        
        # Патчим методы start_monitoring и stop_monitoring
        with patch.object(self.audio_processor, 'start_monitoring'):
            with patch.object(self.audio_processor, 'stop_monitoring'):
                # Включаем мониторинг
                self.audio_processor.toggle_monitoring()
                
                # Проверяем, что мониторинг включен
                self.assertTrue(self.audio_processor.is_monitoring)
                
                # Выключаем мониторинг
                self.audio_processor.toggle_monitoring()
                
                # Проверяем, что мониторинг выключен
                self.assertFalse(self.audio_processor.is_monitoring)
    
    def test_set_monitoring_volume(self):
        """Тест установки громкости мониторинга."""
        # Проверяем начальное значение громкости
        self.assertEqual(self.audio_processor.monitoring_volume, 1.0)
        
        # Устанавливаем новое значение громкости
        self.audio_processor.set_monitoring_volume(0.5)
        
        # Проверяем, что громкость изменилась
        self.assertEqual(self.audio_processor.monitoring_volume, 0.5)
    
    def test_set_low_latency(self):
        """Тест установки режима низкой задержки."""
        # Проверяем начальное значение
        self.assertTrue(self.audio_processor.use_low_latency)
        
        # Выключаем режим низкой задержки
        self.audio_processor.set_low_latency(False)
        
        # Проверяем, что режим изменился
        self.assertFalse(self.audio_processor.use_low_latency)
        
        # Включаем режим низкой задержки
        self.audio_processor.set_low_latency(True)
        
        # Проверяем, что режим изменился
        self.assertTrue(self.audio_processor.use_low_latency)
    
    def test_set_buffer_size(self):
        """Тест установки размера буфера."""
        # Проверяем начальное значение
        self.assertEqual(self.audio_processor.block_size, 128)
        
        # Устанавливаем новый размер буфера
        self.audio_processor.set_buffer_size(256)
        
        # Проверяем, что размер буфера изменился
        self.assertEqual(self.audio_processor.block_size, 256)

if __name__ == '__main__':
    unittest.main() 