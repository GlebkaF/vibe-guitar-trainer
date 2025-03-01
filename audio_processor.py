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
        self.block_size = 128     # Еще меньший размер блока для минимальной задержки
        self.channels = 1         # Количество каналов (моно)
        self.input_channel = 0    # Выбранный входной канал (по умолчанию первый)
        
        # Информация о последнем обнаруженном звуке
        self.last_onset_time = 0
        self.min_time_between_onsets = 0.1  # Минимальное время между обнаружениями (сек)
        self.last_rms = 0.0  # Последнее значение RMS (уровень сигнала)
        
        # Параметры воспроизведения
        self.is_monitoring = False
        self.output_device = None
        self.output_stream = None
        self.monitoring_volume = 1.0  # Громкость мониторинга (0.0 - 1.0)
        
        # Текущее устройство
        self.current_device_info = None
        
        # Инициализация PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = None
        
        # Настройки для минимизации задержки
        self.use_low_latency = True  # Флаг для включения/отключения настроек низкой задержки
        self.low_latency_settings = {
            'input_latency': 0.001,  # Минимальная входная задержка (секунды)
            'output_latency': 0.001  # Минимальная выходная задержка (секунды)
        }
    
    def audio_callback(self, in_data, frame_count, time_info, status):
        """Callback для PyAudio, вызывается при получении аудио-данных"""
        if status:
            print(f"Статус: {status}")
        
        # Преобразуем байты в numpy array
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Отладочная информация о входных данных
        if len(audio_data) > 0:
            max_val = np.max(np.abs(audio_data))
            if max_val > 0.01:  # Выводим только если есть значимый сигнал
                print(f"Входные данные: мин={np.min(audio_data):.4f}, макс={np.max(audio_data):.4f}, среднее={np.mean(audio_data):.4f}, размер={len(audio_data)}")
        
        # Выбираем нужный канал, если устройство многоканальное
        if self.channels > 1:
            # Преобразуем одномерный массив в двумерный с каналами
            audio_data = audio_data.reshape(-1, self.channels)
            # Проверяем, что выбранный канал существует
            channel = min(self.input_channel, self.channels - 1)
            audio_data = audio_data[:, channel]
            print(f"Выбран канал {channel} из {self.channels} каналов")
        
        # Вычисляем RMS (среднеквадратичное значение) как меру громкости
        rms = np.sqrt(np.mean(np.square(audio_data)))
        
        # Всегда сохраняем последнее значение RMS
        self.last_rms = rms
        
        # Если громкость превышает порог и прошло достаточно времени с последнего обнаружения
        current_time = time.time()
        if rms > self.threshold and (current_time - self.last_onset_time) > self.min_time_between_onsets:
            self.last_onset_time = current_time
            print(f"Обнаружен звук: RMS={rms:.4f}")
            
            # Вызываем callback, если он задан
            if self.callback:
                self.callback(current_time, rms)
        
        # Помещаем данные в очередь для обработки в отдельном потоке
        self.audio_queue.put((audio_data, current_time))
        
        # Если включен мониторинг, подготавливаем данные для воспроизведения
        if self.is_monitoring:
            try:
                # Применяем громкость мониторинга
                output_data = audio_data * self.monitoring_volume
                
                # Определяем количество каналов для вывода
                output_channels = 2  # По умолчанию стерео
                if hasattr(self.stream, '_channels'):
                    output_channels = self.stream._channels
                elif hasattr(self.stream, 'channels'):
                    output_channels = self.stream.channels
                
                # Преобразуем в стерео, если нужно
                if output_channels > 1:
                    # Дублируем моно сигнал на все каналы
                    output_data = np.tile(output_data.reshape(-1, 1), (1, output_channels))
                    print(f"Преобразовано в многоканальный формат, форма: {output_data.shape}")
                
                # Возвращаем данные для воспроизведения
                return (output_data.tobytes(), pyaudio.paContinue)
            except Exception as e:
                print(f"Ошибка подготовки данных для воспроизведения: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Если мониторинг выключен или произошла ошибка, возвращаем пустые данные
        # Проверяем, настроен ли поток на вывод
        try:
            # Проверяем, что поток настроен на вывод
            if hasattr(self, 'is_monitoring') and self.is_monitoring:
                # Определяем количество каналов для вывода
                output_channels = 2  # По умолчанию стерео
                if hasattr(self.stream, '_channels'):
                    output_channels = self.stream._channels
                elif hasattr(self.stream, 'channels'):
                    output_channels = self.stream.channels
                
                # Возвращаем тишину
                return (b'\x00' * frame_count * 4 * output_channels, pyaudio.paContinue)
        except Exception as e:
            print(f"Ошибка при подготовке пустых данных: {str(e)}")
        
        return (None, pyaudio.paContinue)
    
    def process_audio_thread(self):
        """Поток обработки аудио"""
        while self.is_running:
            try:
                # Получаем данные из очереди с таймаутом
                audio_data, timestamp = self.audio_queue.get(timeout=0.1)
                
                # Обработка уже перенесена в callback для снижения задержки
                
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
        
        # Всегда сохраняем последнее значение RMS
        self.last_rms = rms
        
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
            
            # Базовые параметры для потока
            stream_params = {
                'format': pyaudio.paFloat32,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'output': False,
                'frames_per_buffer': self.block_size,
                'input_device_index': int(self.current_device_info['index']),
                'stream_callback': self.audio_callback,
                'start': False
            }
            
            # Создаем поток ввода
            self.stream = self.p.open(**stream_params)
            
            self.stream.start_stream()
            print(f"Захват аудио запущен (устройство: {self.current_device_info['name']}, канал: {self.input_channel}, размер буфера: {self.block_size})")
            
            # Запускаем поток воспроизведения, если включен мониторинг
            if self.is_monitoring:
                self.start_monitoring()
                
        except Exception as e:
            self.is_running = False
            print(f"Ошибка запуска захвата аудио: {str(e)}")
            import traceback
            traceback.print_exc()
    
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
            device_info = self.p.get_device_info_by_index(int(device_id))
            channels = int(device_info['maxInputChannels'])
            print(f"Устройство {device_info['name']} имеет {channels} входных каналов")
            return channels
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
            self.current_device_info = self.p.get_device_info_by_index(int(device_id))
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
    
    def set_monitoring_volume(self, volume):
        """Установка громкости мониторинга"""
        self.monitoring_volume = max(0.0, min(1.0, volume))
        print(f"Громкость мониторинга установлена на {self.monitoring_volume:.2f}")
    
    def toggle_monitoring(self):
        """Переключение мониторинга звука"""
        print(f"Переключение мониторинга. Текущее состояние: {self.is_monitoring}")
        if self.is_monitoring:
            print("Выключение мониторинга...")
            self.stop_monitoring()
        else:
            print("Включение мониторинга...")
            self.start_monitoring()
        
        print(f"Новое состояние мониторинга: {self.is_monitoring}")
        return self.is_monitoring
    
    def start_monitoring(self):
        """Запуск мониторинга звука"""
        print("Начало запуска мониторинга...")
        if not self.is_running:
            print("Невозможно запустить мониторинг: обработчик аудио не запущен")
            return False
        
        try:
            # Получаем информацию об устройстве вывода
            print("Получение информации об устройстве вывода...")
            output_device_info = None
            if self.output_device is not None:
                try:
                    print(f"Используется указанное устройство вывода: {self.output_device}")
                    output_device_info = self.p.get_device_info_by_index(self.output_device)
                except Exception as e:
                    print(f"Ошибка получения информации об устройстве вывода: {str(e)}")
            
            if output_device_info is None:
                print("Используется устройство вывода по умолчанию")
                output_device_info = self.p.get_default_output_device_info()
                print(f"Используется устройство вывода по умолчанию: {output_device_info['name']}")
            
            # Закрываем предыдущий поток, если он существует
            if hasattr(self, 'output_stream') and self.output_stream:
                print("Закрытие предыдущего потока вывода...")
                self.output_stream.stop_stream()
                self.output_stream.close()
                self.output_stream = None
            
            # Создаем поток вывода
            output_channels = min(2, output_device_info.get('maxOutputChannels', 2))
            print(f"Количество каналов вывода: {output_channels}")
            
            # Останавливаем текущий поток ввода
            was_running = False
            if self.stream and self.stream.is_active():
                print("Остановка текущего потока ввода...")
                was_running = True
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            
            # Базовые параметры для потока
            print("Настройка параметров потока...")
            stream_params = {
                'format': pyaudio.paFloat32,
                'channels': self.channels,
                'rate': self.sample_rate,
                'input': True,
                'output': True,
                'output_device_index': int(output_device_info['index']),
                'input_device_index': int(self.current_device_info['index']),
                'frames_per_buffer': self.block_size,
                'stream_callback': self.audio_callback,
                'start': False
            }
            print(f"Параметры потока: {stream_params}")
            
            # Создаем новый поток ввода с выводом
            print("Создание нового потока ввода/вывода...")
            self.stream = self.p.open(**stream_params)
            
            print("Запуск потока...")
            self.stream.start_stream()
            self.is_monitoring = True
            print(f"Мониторинг звука запущен (устройство ввода: {self.current_device_info['name']}, устройство вывода: {output_device_info['name']}, громкость: {self.monitoring_volume:.2f}, размер буфера: {self.block_size})")
            return True
        except Exception as e:
            print(f"Ошибка запуска мониторинга звука: {str(e)}")
            import traceback
            traceback.print_exc()
            # Восстанавливаем поток ввода, если он был запущен
            if was_running:
                try:
                    print("Восстановление потока ввода...")
                    # Базовые параметры для потока
                    stream_params = {
                        'format': pyaudio.paFloat32,
                        'channels': self.channels,
                        'rate': self.sample_rate,
                        'input': True,
                        'output': False,
                        'input_device_index': int(self.current_device_info['index']),
                        'frames_per_buffer': self.block_size,
                        'stream_callback': self.audio_callback,
                        'start': False
                    }
                    
                    self.stream = self.p.open(**stream_params)
                    self.stream.start_stream()
                except Exception as e2:
                    print(f"Ошибка восстановления потока ввода: {str(e2)}")
                    import traceback
                    traceback.print_exc()
            
            self.is_monitoring = False
            return False
    
    def stop_monitoring(self):
        """Остановка мониторинга звука"""
        if not self.is_monitoring:
            return False
        
        # Останавливаем текущий поток
        if self.stream and self.stream.is_active():
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        # Закрываем поток вывода, если он существует
        if hasattr(self, 'output_stream') and self.output_stream:
            self.output_stream.stop_stream()
            self.output_stream.close()
            self.output_stream = None
        
        # Базовые параметры для потока
        stream_params = {
            'format': pyaudio.paFloat32,
            'channels': self.channels,
            'rate': self.sample_rate,
            'input': True,
            'output': False,
            'input_device_index': int(self.current_device_info['index']),
            'frames_per_buffer': self.block_size,
            'stream_callback': self.audio_callback,
            'start': False
        }
        
        # Создаем новый поток только для ввода
        try:
            self.stream = self.p.open(**stream_params)
            self.stream.start_stream()
        except Exception as e:
            print(f"Ошибка восстановления потока ввода: {str(e)}")
            import traceback
            traceback.print_exc()
            self.is_running = False
        
        self.is_monitoring = False
        print("Мониторинг звука остановлен")
        return False
    
    def __del__(self):
        """Деструктор класса"""
        self.stop()
        if hasattr(self, 'p'):
            self.p.terminate()