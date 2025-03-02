import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import queue
import time
import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from audio_processor import AudioProcessor

class TestAudioProcessor(unittest.TestCase):
    """Тесты для класса AudioProcessor."""
    
    def setUp(self):
        """Настройка перед каждым тестом."""
        # Создаем мок для PyAudio
        self.pyaudio_patcher = patch('audio_processor.pyaudio.PyAudio')
        self.mock_pyaudio = self.pyaudio_patcher.start()
        
        # Настраиваем мок для PyAudio
        self.mock_pyaudio_instance = self.mock_pyaudio.return_value
        self.mock_pyaudio_instance.get_device_count.return_value = 2
        
        # Мок для устройств
        device_info1 = {'name': 'Test Device 1', 'maxInputChannels': 2}
        device_info2 = {'name': 'Test Device 2', 'maxInputChannels': 1}
        self.mock_pyaudio_instance.get_device_info_by_index.side_effect = [device_info1, device_info2]
        
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
    
    def test_init(self):
        """Тест инициализации AudioProcessor."""
        self.assertEqual(self.audio_processor.threshold, 0.2)
        self.assertEqual(self.audio_processor.callback, self.mock_callback)
        self.assertFalse(self.audio_processor.is_running)
        self.assertIsInstance(self.audio_processor.audio_queue, queue.Queue)
    
    def test_set_threshold(self):
        """Тест установки порога обнаружения звука."""
        self.audio_processor.set_threshold(0.5)
        self.assertEqual(self.audio_processor.threshold, 0.5)
    
    def test_get_input_devices(self):
        """Тест получения списка входных устройств."""
        devices = self.audio_processor.get_input_devices()
        self.assertEqual(len(devices), 2)
        self.mock_pyaudio_instance.get_device_count.assert_called_once()
    
    @patch('audio_processor.threading.Thread')
    def test_start_stop(self, mock_thread):
        """Тест запуска и остановки обработчика аудио."""
        # Настраиваем мок для потока
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance
        
        # Запускаем аудио-процессор
        self.audio_processor.start()
        
        # Проверяем, что поток был создан и запущен
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()
        self.assertTrue(self.audio_processor.is_running)
        
        # Останавливаем аудио-процессор
        self.audio_processor.stop()
        
        # Проверяем, что аудио-процессор остановлен
        self.assertFalse(self.audio_processor.is_running)
        self.mock_stream.close.assert_called_once()
    
    def test_detect_onset(self):
        """Тест обнаружения звука."""
        # Создаем тестовые данные аудио
        # Тихий сигнал (ниже порога)
        quiet_audio = np.zeros(1024, dtype=np.float32)
        quiet_audio[0:100] = 0.1  # Амплитуда ниже порога (0.2)
        
        # Громкий сигнал (выше порога)
        loud_audio = np.zeros(1024, dtype=np.float32)
        loud_audio[0:100] = 0.5  # Амплитуда выше порога (0.2)
        
        # Устанавливаем время последнего обнаружения достаточно давно,
        # чтобы не сработало ограничение на минимальное время между обнаружениями
        self.audio_processor.last_onset_time = time.time() - 1.0
        
        # Проверяем, что тихий сигнал не вызывает обнаружение
        timestamp = time.time()
        
        # Патчим метод np.sqrt, чтобы он возвращал предсказуемое значение для тихого сигнала
        with patch('numpy.sqrt', return_value=0.1):
            # Патчим метод np.mean, чтобы он возвращал значение ниже порога
            with patch('numpy.mean', return_value=0.01):
                self.audio_processor.detect_onset(quiet_audio, timestamp)
                # Проверяем, что callback не был вызван
                self.mock_callback.assert_not_called()
        
        # Сбрасываем мок для callback
        self.mock_callback.reset_mock()
        
        # Проверяем, что громкий сигнал вызывает обнаружение
        timestamp = time.time()
        
        # Патчим метод np.sqrt, чтобы он возвращал предсказуемое значение для громкого сигнала
        with patch('numpy.sqrt', return_value=0.5):
            # Патчим метод np.mean, чтобы он возвращал значение выше порога
            with patch('numpy.mean', return_value=0.25):
                self.audio_processor.detect_onset(loud_audio, timestamp)
                # Проверяем, что callback был вызван
                self.mock_callback.assert_called_once()
                
                # Проверяем аргументы вызова callback
                args, _ = self.mock_callback.call_args
                self.assertEqual(args[0], timestamp)  # Первый аргумент - timestamp
                self.assertEqual(args[1], 0.5)  # Второй аргумент - амплитуда (rms)

if __name__ == '__main__':
    unittest.main() 