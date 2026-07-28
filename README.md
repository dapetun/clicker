# Keyboard Sender

Клавиатурный макрос: крутит выбранные клавиши по кругу, пока не нажмёшь стоп.

## Что умеет

* 8 тем (светлые, тёмные, оранжевая, бирюзовая, красная)
* F6 — старт, F7 — стоп
* Таймер автостопа
* Выбор клавиш через визуальную раскладку
* Работает с русской раскладкой (Win32 keybd_event)
* Сборка в один `.exe` (~5–8 МБ)

## Запуск

```bash
pip install -r requirements.txt
python main.py
```

## Сборка .exe

```bash
pyinstaller main.spec
```

## Стек

Python 3.13+, CustomTkinter, keyboard, PyInstaller
