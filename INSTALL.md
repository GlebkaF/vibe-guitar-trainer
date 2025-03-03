# Инструкция по установке и запуску Guitar Rhythm Trainer

## Системные требования

- Python 3.10 или новее
- Аудиоинтерфейс для подключения гитары
- Операционная система: Windows, macOS или Linux

## Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/vibe-guitar-trainer.git
cd vibe-guitar-trainer
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
```

### 3. Активация виртуального окружения

#### Windows:

```bash
venv\Scripts\activate
```

#### macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Установка зависимостей

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Запуск приложения

```bash
python main.py
```

## Использование

1. Подключите гитару к компьютеру через аудиоинтерфейс.
2. Выберите устройство ввода (вход) из выпадающего списка.
3. Выберите нужный входной канал, к которому подключена гитара.
4. Выберите устройство вывода (выход) из выпадающего списка.
5. Включите мониторинг звука, чтобы слышать звук гитары через выбранное устройство вывода.
6. Настройте темп (BPM) с помощью ползунка.
7. Настройте порог громкости в зависимости от вашей гитары.
8. Нажмите кнопку "Старт" для начала тренировки.
9. Играйте на гитаре в такт метронома.
10. Следите за индикатором обратной связи:
    - Зеленый цвет — играете в ритм.
    - Красный цвет — играете не в ритм.
11. Отслеживайте свою точность в процентах.

## Функции приложения

### Выбор входного канала

Многие аудиоинтерфейсы имеют несколько входных каналов. Приложение позволяет выбрать конкретный канал, к которому подключена гитара:

1. Сначала выберите устройство ввода (аудиоинтерфейс)
2. Затем выберите нужный канал из выпадающего списка "Канал"
3. Для гитары обычно используется инструментальный вход (Hi-Z)

Примеры типичных подключений:

- Электрогитара: обычно подключается к каналу 1 (инструментальный вход)
- Микрофон: обычно подключается к микрофонному входу (XLR)
- Линейный сигнал: подключается к линейному входу

### Мониторинг звука

Функция мониторинга позволяет слышать звук гитары через выбранное устройство вывода в реальном времени. Это полезно для:

- Проверки правильности подключения гитары
- Настройки громкости и тона гитары
- Контроля звучания во время тренировки

Для использования мониторинга:

1. Выберите устройство вывода (например, наушники или колонки)
2. Включите переключатель "Мониторинг"
3. Проверьте звук, сыграв несколько нот на гитаре

### Выбор устройств ввода/вывода

Приложение позволяет выбрать:

- **Устройство ввода** - аудиоинтерфейс или микрофон, к которому подключена гитара
- **Устройство вывода** - наушники, колонки или другое устройство для воспроизведения звука

## Решение проблем

### Не обнаруживаются аудиоустройства

Убедитесь, что ваш аудиоинтерфейс правильно подключен и распознан системой. Проверьте настройки звука в операционной системе.

### Нет звука метронома

Убедитесь, что файл `click.wav` находится в той же директории, что и `main.py`.

### Не работает мониторинг звука

1. Проверьте, правильно ли выбраны устройства ввода и вывода.
2. Убедитесь, что на устройстве вывода включен звук и установлена достаточная громкость.
3. Проверьте, что гитара подключена и производит сигнал.
4. Попробуйте перезапустить приложение после подключения всех устройств.

### Приложение не реагирует на звук гитары

1. Проверьте, правильно ли выбрано устройство ввода.
2. Убедитесь, что выбран правильный входной канал, к которому подключена гитара.
3. Настройте порог громкости (уменьшите значение, если звук не обнаруживается).
4. Убедитесь, что гитара подключена и звук проходит через аудиоинтерфейс.
5. Включите мониторинг, чтобы проверить, поступает ли звук с гитары.

## Дополнительная информация

Для получения дополнительной информации обратитесь к файлу README.md.
