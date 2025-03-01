import numpy as np
import pyaudio
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
        self.input_channel = 0    # Выбранный входной канал (по умолчанию первый)
        
        # Информация о последнем обнаруженном звуке
        self.last_onset_time = 0
        self.min_time_between_onsets = 0.1  # Минимальное время между обнаружениями (сек)
        
        # Параметры воспроизведения
        self.is_monitoring = False
        self.output_device = None
        self.output_stream = None
        
        # Текущее устройство
        self.current_device_info = None
        
        # Инициализация PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback для PyAudio, вызывается при получении аудио-данных"""
        if status:
            print(f"Статус: {status}")
        
        # Преобразуем байты в numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Выбираем нужный канал, если устройство многоканальное
        if self.channels > 1:
            # Преобразуем одномерный массив в двумерный с каналами
            audio_data = audio_data.reshape(-1, self.channels)
            # Проверяем, что выбранный канал существует
            channel = min(self.input_channel, self.channels - 1)
            audio_data = audio_data[:, channel]
        
        # Помещаем данные в очередь для обработки в отдельном потоке
        self.audio_queue.put((audio_data, time.time()))
        
        # Если включен мониторинг, воспроизводим звук
        if self.is_monitoring and self.output_stream:
            try:
                # Преобразуем обратно в стерео, если нужно
                if self.output_stream._channels > 1:
                    output_data = np.column_stack((audio_data, audio_data))
                else:
                    output_data = audio_data
                
                # Воспроизводим звук
                return (output_data.tobytes(), pyaudio.paContinue)
            except Exception as e:
                print(f"Ошибка воспроизведения звука: {str(e)}")
        
        return (None, pyaudio.paContinue)
    
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
            # Получаем информацию о текущем устройстве
            if self.current_device_info is None:
                # Используем устройство по умолчанию
                self.current_device_info = self.p.get_default_input_device_info()
                print(f"Используется устройство по умолчанию: {self.current_device_info['name']}")
            
            # Определяем количество каналов
            self.channels = self.current_device_info.get('maxInputChannels', 1)
            
            # Создаем поток ввода
            self.stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                output=False,
                frames_per_buffer=self.block_size,
                input_device_index=int(self.current_device_info['index']),
                stream_callback=self.audio_callback
            )
            
            self.stream.start_stream()
            print(f"Захват аудио запущен (устройство: {self.current_device_info['name']}, канал: {self.input_channel})")
            
            # Запускаем поток воспроизведения, если включен мониторинг
            if self.is_monitoring:
                self.start_monitoring()
                
        except Exception as e:
            self.is_running = False
            print(f"Ошибка запуска захвата аудио: {str(e)}")
    
    def stop(self):
        """Остановка обработки аудио"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Останавливаем поток захвата аудио
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Останавливаем поток воспроизведения
        self.stop_monitoring()
        
        # Ждем завершения потока обработки
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        
        print("Захват аудио остановлен")
    
    def set_threshold(self, threshold):
        """Установка порога громкости"""
        self.threshold = max(0.0, min(1.0, threshold))
    
    def get_input_devices(self):
        """Получение списка доступных устройств ввода"""
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append(device_info)
        return devices
    
    def get_output_devices(self):
        """Получение списка доступных устройств вывода"""
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                devices.append(device_info)
        return devices
    
    def get_device_channels(self, device_id):
        """Получение количества каналов устройства"""
        try:
            device_info = self.p.get_device_info_by_index(device_id)
            return device_info['maxInputChannels']
        except Exception as e:
            print(f"Ошибка получения информации об устройстве: {str(e)}")
            return 1
    
    def set_device(self, device_id):
        """Установка устройства ввода"""
        was_running = self.is_running
        
        # Останавливаем, если запущено
        if was_running:
            self.stop()
        
        # Устанавливаем устройство
        try:
            self.current_device_info = self.p.get_device_info_by_index(device_id)
            print(f"Выбрано устройство: {self.current_device_info['name']} с {self.current_device_info['maxInputChannels']} входными каналами")
        except Exception as e:
            print(f"Ошибка получения информации об устройстве: {str(e)}")
            self.current_device_info = None
        
        # Сбрасываем выбранный канал на первый
        self.input_channel = 0
        
        # Перезапускаем, если было запущено
        if was_running:
            self.start()
    
    def set_input_channel(self, channel):
        """Установка входного канала"""
        if self.current_device_info and channel < self.current_device_info['maxInputChannels']:
            self.input_channel = channel
            print(f"Выбран входной канал: {channel}")
            return True
        else:
            print(f"Ошибка: канал {channel} не существует для текущего устройства")
            return False
    
    def set_output_device(self, device_id):
        """Установка устройства вывода"""
        was_monitoring = self.is_monitoring
        
        # Останавливаем мониторинг, если запущен
        if was_monitoring:
            self.stop_monitoring()
        
        # Устанавливаем устройство
        self.output_device = device_id
        
        # Перезапускаем мониторинг, если был запущен
        if was_monitoring:
            self.start_monitoring()
    
    def toggle_monitoring(self):
        """Переключение мониторинга звука"""
        if self.is_monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
        
        return self.is_monitoring
    
    def start_monitoring(self):
        """Запуск мониторинга звука"""
        if not self.is_running:
            return False
        
        try:
            # Получаем информацию об устройстве вывода
            output_device_info = self.p.get_device_info_by_index(self.output_device) if self.output_device is not None else self.p.get_default_output_device_info()
            
            # Создаем поток вывода
            self.output_stream = self.p.open(
                format=pyaudio.paFloat32,
                channels=2,  # Стерео выход
                rate=self.sample_rate,
                output=True,
                input=False,
                frames_per_buffer=self.block_size,
                output_device_index=int(output_device_info['index'])
            )
            
            self.output_stream.start_stream()
            self.is_monitoring = True
            print(f"Мониторинг звука запущен (устройство: {output_device_info['name']})")
            return True
        except Exception as e:
            print(f"Ошибка запуска мониторинга звука: {str(e)}")
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self):
        """Остановка мониторинга звука"""
        if hasattr(self, 'output_stream') and self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        self.is_monitoring = False
        print("Мониторинг звука остановлен")
        return False
    
    def __del__(self):
        """Деструктор класса"""
        self.stop()
        if hasattr(self, 'p'):
            self.p.terminate()