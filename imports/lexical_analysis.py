from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor, QStandardItem, QStandardItemModel
from PyQt5 import uic
import json
import re

# Método helper encargado de cargar los tokens en memoria.

def load_tokens(path: str) -> dict:
    with open(path, 'r') as json_file:
        return json.load(json_file)

# Clase principal de la interfaz gráfica.

class lexical_analysis(QMainWindow):

    # Constructor de nuestro objeto.

    def __init__(self):
        super(lexical_analysis, self).__init__()
        uic.loadUi('graphics/main_window.ui', self) # Carga de nuestra interfaz de QtDesigner.
        self.setWindowTitle('Lexical Analysis GUI')

        # Conexión de métodos con botones 'compile' y 'load file'.

        self.load_file_button.clicked.connect(self.load_file)
        self.compile_button.clicked.connect(self.compile_code)

        # Carga de tokens válidos en el compilador (C++) en memoria.

        self.keywords: dict = load_tokens('tokens/keywords.json')
        self.punctuation: dict = load_tokens('tokens/punctuation.json')
        self.operators: dict = load_tokens('tokens/operators.json')

    # Método encargado de permitir la carga de archivos locales.

    def load_file(self) -> None:
        
        file_filter = "Archivos C++ (*.cpp *.hpp *.h);;Todos los archivos (*)"
        file_dialog = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', file_filter)

        if file_dialog[0]:
            with open(file_dialog[0], 'r', encoding = 'utf-8') as file:
                file_content = file.read()
                self.code_display.setPlainText(file_content)

    # TODO: Es el método que arrojará los logs y hará el analisis.

    def compile_code(self) -> None:

        code_text = self.code_display.toPlainText()
        pattern = r'\b(int|char|if|else|while|for|return|[a-zA-Z_]\w*|\d+|[;,.(){}\[\]])\b'

        tokens = re.findall(pattern, code_text)

        keywords = load_tokens('tokens/keywords.json')
        punctuation = load_tokens('tokens/punctuation.json')
        operators = load_tokens('tokens/operators.json')

        model = QStandardItemModel()
        self.token_view.setModel(model)

        found_tokens: int = 0

        for token in tokens:
            if token in keywords:
                category = keywords[token]
            elif token in punctuation:
                category = punctuation[token]
            elif token in operators:
                category = operators[token]
            else:
                category = 'Identificador o Constante'

            token_item = QStandardItem(token)
            category_item = QStandardItem(category)

            model.appendRow([token_item, category_item])
            found_tokens += 1

        green_color = QColor(0, 255, 0)
        green_format = QTextCharFormat()
        green_format.setForeground(green_color)

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(green_format)
        cursor.insertText(f"Tokens encontrados: {found_tokens}" + '\n')