import time
import numpy as np

class RhythmAnalyzer:
    def __init__(self, tolerance=0.1):
        """
        Инициализация анализатора ритма
        
        Args:
            tolerance: Допустимое отклонение от идеального ритма (в секундах)
        """
        self.tolerance = tolerance
        self.is_active = False
        
        # Метроном
        self.tempo = 80  # BPM (ударов в минуту)
        self.beat_interval = 60.0 / self.tempo  # Интервал между ударами (в секундах)
        self.last_metronome_beat = 0
        
        # Статистика
        self.total_hits = 0
        self.accurate_hits = 0
        self.accuracy = 0.0
    
    def set_tempo(self, tempo):
        """Установка темпа метронома"""
        self.tempo = max(40, min(220, tempo))  # Ограничиваем темп в разумных пределах
        self.beat_interval = 60.0 / self.tempo
    
    def start(self):
        """Запуск анализатора ритма"""
        self.is_active = True
        self.last_metronome_beat = time.time()
        self.reset_stats()
    
    def stop(self):
        """Остановка анализатора ритма"""
        self.is_active = False
    
    def reset_stats(self):
        """Сброс статистики"""
        self.total_hits = 0
        self.accurate_hits = 0
        self.accuracy = 0.0
    
    def update_metronome(self, current_time):
        """
        Обновление состояния метронома
        
        Args:
            current_time: Текущее время
            
        Returns:
            bool: True, если произошел удар метронома
        """
        if not self.is_active:
            return False
        
        # Проверяем, должен ли произойти удар метронома
        time_since_last_beat = current_time - self.last_metronome_beat
        
        if time_since_last_beat >= self.beat_interval:
            # Вычисляем, сколько ударов должно было произойти
            beats_to_add = int(time_since_last_beat / self.beat_interval)
            self.last_metronome_beat += beats_to_add * self.beat_interval
            return True
        
        return False
    
    def analyze_hit(self, hit_time):
        """
        Анализ попадания в ритм
        
        Args:
            hit_time: Время удара (в секундах)
            
        Returns:
            tuple: (is_accurate, deviation) - точность попадания и отклонение от идеального времени
        """
        if not self.is_active:
            return False, 0.0
        
        # Увеличиваем счетчик ударов
        self.total_hits += 1
        
        # Находим ближайший ожидаемый удар метронома
        time_since_last_beat = hit_time - self.last_metronome_beat
        beats_since_last = time_since_last_beat / self.beat_interval
        
        # Определяем, к какому удару метронома ближе всего текущий удар
        closest_beat_offset = round(beats_since_last) * self.beat_interval
        expected_time = self.last_metronome_beat + closest_beat_offset
        
        # Вычисляем отклонение от идеального времени
        deviation = abs(hit_time - expected_time)
        
        # Определяем, попал ли удар в допустимый интервал
        is_accurate = deviation <= self.tolerance
        
        # Обновляем статистику
        if is_accurate:
            self.accurate_hits += 1
        
        if self.total_hits > 0:
            self.accuracy = self.accurate_hits / self.total_hits
        
        return is_accurate, deviation
    
    def get_next_beat_time(self):
        """
        Получение времени следующего удара метронома
        
        Returns:
            float: Время следующего удара метронома (в секундах)
        """
        if not self.is_active:
            return 0.0
        
        return self.last_metronome_beat + self.beat_interval
    
    def get_beat_phase(self, current_time):
        """
        Получение фазы текущего удара (от 0.0 до 1.0)
        
        Args:
            current_time: Текущее время
            
        Returns:
            float: Фаза удара (0.0 - начало, 1.0 - конец)
        """
        if not self.is_active:
            return 0.0
        
        time_since_last_beat = current_time - self.last_metronome_beat
        phase = (time_since_last_beat % self.beat_interval) / self.beat_interval
        return phase
    
    def get_stats(self):
        """
        Получение статистики
        
        Returns:
            dict: Статистика точности
        """
        return {
            'total_hits': self.total_hits,
            'accurate_hits': self.accurate_hits,
            'accuracy': self.accuracy,
            'tempo': self.tempo
        } 