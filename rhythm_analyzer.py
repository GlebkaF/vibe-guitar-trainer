import time
import numpy as np

class RhythmAnalyzer:
    def __init__(self, tolerance=0.1):
        """
        Инициализация анализатора ритма
        
        Args:
            tolerance: Допустимое отклонение от идеального ритма (в долях)
        """
        self.tolerance = tolerance
        self.is_running = False
        
        # Параметры ритма
        self.tempo = 80  # BPM (ударов в минуту)
        self.beat_interval = 60.0 / self.tempo  # Интервал между ударами (сек)
        self.last_beat_time = 0
        
        # Статистика
        self.total_hits = 0
        self.accurate_hits = 0
        self.deviations = []
    
    def start(self):
        """Запуск анализатора ритма"""
        self.is_running = True
        self.last_beat_time = time.time()
        
        # Сбрасываем статистику
        self.total_hits = 0
        self.accurate_hits = 0
        self.deviations = []
    
    def stop(self):
        """Остановка анализатора ритма"""
        self.is_running = False
    
    def set_tempo(self, tempo):
        """
        Установка темпа
        
        Args:
            tempo: Темп в BPM (ударов в минуту)
        """
        self.tempo = max(40, min(220, tempo))  # Ограничиваем темп в разумных пределах
        self.beat_interval = 60.0 / self.tempo
    
    def analyze_hit(self, hit_time):
        """
        Анализ попадания в ритм
        
        Args:
            hit_time: Время удара (timestamp)
        
        Returns:
            tuple: (is_accurate, deviation)
                is_accurate: Точное ли попадание в ритм
                deviation: Отклонение от идеального ритма (в долях)
        """
        if not self.is_running:
            return False, 0.0
        
        # Вычисляем, сколько ударов должно было пройти с начала
        elapsed_time = hit_time - self.last_beat_time
        expected_beats = elapsed_time / self.beat_interval
        
        # Ближайший целый удар
        nearest_beat = round(expected_beats)
        
        # Отклонение от идеального ритма (в долях)
        deviation = abs(expected_beats - nearest_beat)
        
        # Определяем, точное ли попадание
        is_accurate = deviation <= self.tolerance
        
        # Обновляем статистику
        self.total_hits += 1
        if is_accurate:
            self.accurate_hits += 1
        self.deviations.append(deviation)
        
        return is_accurate, deviation
    
    def get_stats(self):
        """
        Получение статистики
        
        Returns:
            dict: Статистика анализа ритма
        """
        accuracy = self.accurate_hits / max(1, self.total_hits)
        avg_deviation = np.mean(self.deviations) if self.deviations else 0.0
        
        return {
            'total_hits': self.total_hits,
            'accurate_hits': self.accurate_hits,
            'accuracy': accuracy,
            'avg_deviation': avg_deviation
        } 