from pydub import AudioSegment
import os

def convert_opus_to_wav(opus_file, wav_file):
    """Конвертирует файл .opus в .wav"""
    try:
        # Проверяем, существует ли файл .opus
        if not os.path.exists(opus_file):
            print(f"Файл {opus_file} не найден")
            return False
        
        # Загружаем файл .opus
        print(f"Загружаем файл {opus_file}...")
        sound = AudioSegment.from_file(opus_file)
        
        # Сохраняем в формате .wav
        print(f"Сохраняем в формате .wav: {wav_file}")
        sound.export(wav_file, format="wav")
        
        print(f"Конвертация завершена: {opus_file} -> {wav_file}")
        return True
    except Exception as e:
        print(f"Ошибка при конвертации: {str(e)}")
        return False

if __name__ == "__main__":
    # Пути к файлам
    opus_file = "tack.opus"
    wav_file = "tack.wav"
    
    # Конвертируем файл
    convert_opus_to_wav(opus_file, wav_file) 