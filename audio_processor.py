import numpy as np
import sounddevice as sd
import threading
import time
import queue

class AudioProcessor:
    def __init__(self, callback=None, threshold=0.1):
        """
        Инициализация обработчика аудио
        
        Args:
            callback: Функция обратного вызова, вызывается при обнаружении звука
            threshold: Порог громкости для обнаружения звука (0.0 - 1.0)
        """
        self.callback = callback
        self.threshold = threshold
        self.is_running = False
        self.audio_queue = queue.Queue()
        self.thread = None
        
        # Параметры аудио
        self.sample_rate = 44100  # Частота дискретизации (Гц)
        self.block_size = 1024    # Размер блока (сэмплы)
        self.channels = 1         # Количество каналов (моно)
        
        # Информация о последнем обнаруженном звуке
        self.last_onset_time = 0
        self.min_time_between_onsets = 0.1  # Минимальное время между обнаружениями (сек)
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback для sounddevice, вызывается при получении аудио-данных"""
        if status:
            print(f"Статус: {status}")
        
        # Преобразуем в моно, если нужно
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]
        
        # Помещаем данные в очередь для обработки в отдельном потоке
        self.audio_queue.put((audio_data, time.time()))
    
    def process_audio_thread(self):
        """Поток обработки аудио"""
        while self.is_running:
            try:
                # Получаем данные из очереди с таймаутом
                audio_data, timestamp = self.audio_queue.get(timeout=0.5)
                
                # Обнаружение начала звука (onset detection)
                self.detect_onset(audio_data, timestamp)
                
                self.audio_queue.task_done()
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Ошибка обработки аудио: {str(e)}")
    
    def detect_onset(self, audio_data, timestamp):
        """
        Обнаружение начала звука (onset detection)
        
        Args:
            audio_data: Аудио-данные (numpy array)
            timestamp: Временная метка получения данных
        """
        # Вычисляем RMS (среднеквадратичное значение) как меру громкости
        rms = np.sqrt(np.mean(np.square(audio_data)))
        
        # Если громкость превышает порог и прошло достаточно времени с последнего обнаружения
        current_time = timestamp
        if rms > self.threshold and (current_time - self.last_onset_time) > self.min_time_between_onsets:
            self.last_onset_time = current_time
            
            # Вызываем callback, если он задан
            if self.callback:
                self.callback(current_time, rms)
    
    def start(self):
        """Запуск обработки аудио"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Запускаем поток обработки
        self.thread = threading.Thread(target=self.process_audio_thread)
        self.thread.daemon = True
        self.thread.start()
        
        # Запускаем поток захвата аудио
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=self.channels,
                callback=self.audio_callback
            )
            self.stream.start()
            print("Захват аудио запущен")
        except Exception as e:
            self.is_running = False
            print(f"Ошибка запуска захвата аудио: {str(e)}")
    
    def stop(self):
        """Остановка обработки аудио"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Останавливаем поток захвата аудио
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        # Ждем завершения потока обработки
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        print("Захват аудио остановлен")
    
    def set_threshold(self, threshold):
        """Установка порога громкости"""
        self.threshold = max(0.0, min(1.0, threshold))
    
    def get_input_devices(self):
        """Получение списка доступных устройств ввода"""
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        return input_devices
    
    def set_device(self, device_id):
        """Установка устройства ввода"""
        was_running = self.is_running
        
        # Останавливаем, если запущено
        if was_running:
            self.stop()
        
        # Устанавливаем устройство
        sd.default.device = device_id
        
        # Перезапускаем, если было запущено
        if was_running:
            self.start() 