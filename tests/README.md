# Тесты для Guitar Trainer

В этой директории находятся тесты для приложения Guitar Trainer.

## Структура тестов

- `test_audio_processor.py` - тесты для класса `AudioProcessor`, который отвечает за обработку аудио
- `test_audio_processing.py` - тесты для функциональности обработки аудио
- `test_rhythm_trainer.py` - тесты для компонентов ритм-тренера
- `test_metronome.py` - тесты для функциональности метронома
- `run_tests.py` - скрипт для запуска всех тестов

## Запуск тестов

### Запуск всех тестов

```bash
python3 run_tests.py
```

### Запуск отдельных тестов

```bash
# Запуск тестов для AudioProcessor
python3 -m unittest test_audio_processor.py

# Запуск тестов для обработки аудио
python3 -m unittest test_audio_processing.py

# Запуск тестов для ритм-тренера
python3 -m unittest test_rhythm_trainer.py

# Запуск тестов для метронома
python3 -m unittest test_metronome.py
```

### Запуск отдельного теста

```bash
python3 -m unittest test_audio_processor.TestAudioProcessor.test_init
```

## Примечания

Тесты для GUI-компонентов могут не работать из-за сложности мокирования Kivy. Рекомендуется запускать только тесты для `AudioProcessor`, которые не зависят от GUI.

## Добавление новых тестов

При добавлении новых тестов следуйте следующим правилам:

1. Создайте новый файл с префиксом `test_` и суффиксом `.py`
2. Импортируйте необходимые модули и классы
3. Создайте класс, наследующийся от `unittest.TestCase`
4. Добавьте методы с префиксом `test_`
5. Используйте методы `setUp` и `tearDown` для настройки и очистки перед и после каждого теста

Пример:

```python
import unittest
from unittest.mock import MagicMock, patch

class TestMyClass(unittest.TestCase):
    def setUp(self):
        # Настройка перед каждым тестом
        pass

    def tearDown(self):
        # Очистка после каждого теста
        pass

    def test_my_method(self):
        # Тест для метода
        pass
```
