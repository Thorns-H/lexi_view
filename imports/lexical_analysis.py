from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QTextCharFormat, QTextCursor, QColor, QStandardItem, QStandardItemModel
from PyQt5 import uic
import json
import re
import time

# Método helper encargado de cargar los tokens en memoria.

def load_tokens(path: str) -> dict:
    with open(path, 'r') as json_file:
        return json.load(json_file)
    
# Método helper para separar las tuplas en las expresiones.

def get_token(tupla) -> str:
    for token in tupla:
        if token != '':
            return token
    return None 

# Clase principal de la interfaz gráfica.

class lexical_analysis(QMainWindow):

    # Constructor de nuestro objeto.

    def __init__(self):
        super(lexical_analysis, self).__init__()
        uic.loadUi('graphics/main_window.ui', self) # Carga de nuestra interfaz de QtDesigner.
        self.setWindowTitle('Lexi View')

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

    # Es el método que arrojará los logs y hará el analisis.

    def compile_code(self) -> None:

        start_time = time.time()

        code_text = self.code_display.toPlainText()
        pattern = r'(\>\>|\"|\#|\[|\]|\,|\;|\:|\.|\-\>|\.\.\.|\:\:|\{|\}|\=|\+\+|\+|\-\-|\-|\*|\/|\%|\=\=|\!\=|\<|\>|\<\=|\>\=|\&\&|\|\||!|&|\||\^|~|<<|>>)|(\b[a-zA-Z_]\w*|\d+)\b'

        # Encontramos todas las tuplas con tokens.

        tokens = re.findall(pattern, code_text)

        converted_tokens: list = []

        # Obtenemos todos los tokens separados.

        for token in tokens:
            converted_tokens.append(get_token(token))

        model = QStandardItemModel()
        self.token_view.setModel(model)

        found_tokens: int = 0

        # Clasificamos los tokens según los json pertenecientes.

        for token in converted_tokens:
            if token in self.keywords:
                category = self.keywords[token]
            elif token in self.punctuation:
                category = self.punctuation[token]
            elif token in self.operators:
                category = self.operators[token]
            else:
                category = 'Identificador o Constante'

            token_item = QStandardItem(token)
            category_item = QStandardItem(category)

            model.appendRow([token_item, category_item])
            found_tokens += 1

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        end_time = time.time()

        # Mostramos los logs de los tokens encontrados en el codigo cargado en la gui.

        cursor.insertText(f"Found {found_tokens} tokens in {end_time - start_time:.5f}s" + '\n')