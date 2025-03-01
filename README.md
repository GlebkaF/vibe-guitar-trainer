# 🎸 Guitar Rhythm Trainer (Тренажер ритма для гитары)

Guitar Rhythm Trainer — это MVP-приложение, помогающее музыкантам улучшать свои навыки игры на электрогитаре. Оно проигрывает метроном и проверяет попадание пользователя в ритм, отображая результат визуально.

## 💡 Идея приложения:

- Пользователь подключает электрогитару через аудиоинтерфейс.
- Приложение проигрывает метроном и визуально показывает текущий ритм.
- Пользователь играет на гитаре в такт метронома.
- Приложение считывает звук с гитары и показывает обратную связь:
  - ✅ Зеленый цвет — играете в ритм.
  - ❌ Красный цвет — играете не в ритм.

---

## 🚀 Технический стек (кросс-платформенный MVP):

- **Язык**: Python 3.x
- **GUI-фреймворк**: [Kivy](https://kivy.org/) (кроссплатформенный интерфейс)
- **Аудио-обработка**:
  - Захват звука с гитары: [sounddevice](https://python-sounddevice.readthedocs.io/) или [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/)
  - Анализ сигнала и ритма: [Librosa](https://librosa.org/doc/latest/index.html), [numpy/scipy](https://numpy.org/)
- **Кроссплатформенность (Desktop + Mobile)**:
  - Android: Buildozer
  - iOS: Kivy-iOS, XCode
- **Дополнительно**: OpenAI SDK (для взаимодействия и помощи с разработкой при необходимости)

---

## ✅ Быстрый старт разработки (через Cursor):

### 👉 Установка зависимостей:

Создайте виртуальное окружение и активируйте его:

```bash
python3 -m venv venv
source venv/bin/activate  # Для Windows используйте venv\Scripts\activate
```

Установите зависимости:

```bash
pip install --upgrade pip
pip install kivy librosa sounddevice numpy scipy matplotlib
```

> ℹ️ **Рекомендуемая версия Python:** Python 3.10 или новее.

### 🎯 Запуск приложения:

Создайте основной файл `main.py` и импортируйте Kivy, sounddevice и librosa:

```python
# main.py
import kivy
from kivy.app import App
from kivy.uix.label import Label

class GuitarTrainerApp(App):
    def build(self):
        return Label(text='🎸 Guitar Rhythm Trainer')

if __name__ == '__main__':
    GuitarTrainerApp().run()
```

Запустите приложение командой:

```bash
python main.py
```

Вы должны увидеть окно с простым текстом "🎸 Guitar Rhythm Trainer". Теперь можно постепенно добавлять функционал.

---

## 📦 Сборка мобильного приложения (Android):

Используйте Buildozer:

```bash
pip install cython buildozer
buildozer init
```

Измените файл `buildozer.spec`:

```ini
requirements = python3, kivy, numpy, librosa, sounddevice
android.permissions = RECORD_AUDIO
```

Затем запустите для Android:

```bash
buildozer -v android debug
```

После успешной сборки устанавливайте APK:

```bash
buildozer android deploy run
```

---

## 🍏 Сборка мобильного приложения (iOS):

Используйте Kivy-iOS и XCode (на MacOS):

```bash
pip install cython kivy-ios
toolchain build python3 kivy
toolchain create GuitarTrainer ../GuitarTrainer
```

После создания проекта откройте проект `.xcodeproj` в папке XCode и соберите приложение через XCode.

---

## 🧠 Поддержка LLM (ваш Workflow с Cursor):

- Используйте Cursor или любой другой AI-редактор для:
  - Генерации отдельных блоков функционала.
  - Решения возникающих проблем.
  - Автоматического исправления ошибок и оптимизации кода.

---

## 🔖 Roadmap MVP:

Короткий план итеративной разработки:

1. ✅ Настроить среду Kivy.
2. 👈 Создать простой UI c визуальным метрономом.
3. 🔉 Подключение гитары через аудио-интерфейс (sounddevice).
4. 🎼 Добавить анализ сигнала на попадание в ритм (через Librosa и numpy/scipy).
5. 🎨 Реализовать визуальную обратную связь (зеленый/красный индикатор).
6. 📱 Сборка мобильных версий (Buildozer для Android, Kivy-iOS для iOS).

---

## 📚 Полезные ссылки:

- [Документация Kivy](https://kivy.org/doc/stable/)
- [Sounddevice (захват аудио)](https://python-sounddevice.readthedocs.io/)
- [Librosa (анализ аудио-сигналов)](https://librosa.org/doc/latest/index.html)
- [Buildozer (упаковка под мобильные платформы)](https://github.com/kivy/buildozer)
- [Kivy-iOS (упаковка под iOS)](https://github.com/kivy/kivy-ios)
