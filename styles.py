GLOBAL_STYLE = """QMainWindow {
    background-color: #f5f5f5;
}

QWidget {
    font-family: 'Segoe UI', Tahoma, sans-serif;
    font-size: 14px;
    color: #333333;
}

QLabel {
    background-color: transparent;
    background: transparent;
}

QPushButton {
    background-color: #4a90e2;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QPushButton:hover {
    background-color: #357abd;
}

QPushButton#PrimaryButton {
    background-color: #4a90e2;
    color: white;
    font-weight: bold;
}

QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox {
    border: 1px solid #dddddd;
    border-radius: 3px;
    padding: 4px;
    background-color: white;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}

QSpinBox::up-button, QSpinBox::down-button {
    width: 0;
    height: 0;
}

QLabel#Title {
    font-family: 'Segoe UI', sans-serif;
    font-size: 17px;
    font-weight: bold;
    color: #2c3e50;
    background: transparent;
}

QLabel#Subtitle {
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
    color: #555555;
    background: transparent;
}

QLabel#Secondary {
    font-family: 'Segoe UI', sans-serif;
    color: #555555;
    font-size: 12px;
    background: transparent;
}

QLabel#Body {
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    color: #333333;
    background: transparent;
}

QFrame#Card {
    background-color: white;
    border-radius: 8px;
    border: 1px solid #eeeeee;
}
"""

WINDOW_WIDTH = 580
WINDOW_HEIGHT = 400
