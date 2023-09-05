from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
import json

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
        self.arithmetic_operators: dict = load_tokens('tokens/arithmetic_operators.json')

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
        ...
