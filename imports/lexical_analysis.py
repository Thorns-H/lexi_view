from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtGui import QTextCursor, QStandardItem, QStandardItemModel
from PyQt5 import uic

from antlr4 import InputStream, CommonTokenStream
from antlr4.error.ErrorListener import ConsoleErrorListener
from CPP14Lexer import CPP14Lexer
from CPP14Parser import CPP14Parser

import json
import time
import re

"""
from PIL import Image, ImageTk
import antlr4
import re
import subprocess
import pygraphviz as pgv
import tkinter as tk
"""

# Método helper encargado de cargar los tokens en memoria.

def load_tokens(path: str) -> dict:
    with open(path, 'r') as json_file:
        return json.load(json_file)
    
# Método helper para separar las tuplas en las expresiones.

def get_token(expressions: tuple) -> str:
    for token in expressions:
        if token != '':
            return token
    return None 

# Clase principal de la interfaz gráfica.

class lexical_analysis(QMainWindow):

    # Constructor de nuestro objeto.

    def __init__(self) -> None:
        super(lexical_analysis, self).__init__()
        uic.loadUi('graphics/main_window.ui', self) # Carga de nuestra interfaz de QtDesigner.
        self.setWindowTitle('Lexi View')

        self.error_listener = MyErrorListener(self.logs_display)

        # Conexión de métodos con botones 'compile' y 'load file'.

        self.load_file_button.clicked.connect(self.load_file)
        self.compile_button.clicked.connect(self.compile_code)

        # Carga de tokens válidos en el compilador (C++) en memoria.

        self.keywords: dict = load_tokens('tokens/keywords.json')
        self.punctuation: dict = load_tokens('tokens/punctuation.json')
        self.operators: dict = load_tokens('tokens/operators.json')

        # Cargamos los patrones de tipos de datos.

        self.integer_pattern = re.compile(r'\b\d+\b')
        self.float_pattern = re.compile(r'\b\d+\.\d+\b')
        self.string_pattern = re.compile(r'(\'[^\']*\'|\"[^\"]*\")')

    # Método encargado de permitir la carga de archivos locales.

    def load_file(self) -> None:
        
        file_filter = "Archivos C++ / Tokens (*.cpp *.hpp *.h);;Todos los archivos (*)"
        file_dialog = QFileDialog.getOpenFileName(self, 'Seleccionar archivo', '', file_filter)

        if file_dialog[0]:
            with open(file_dialog[0], 'r', encoding = 'utf-8') as file:
                file_content = file.read()
                self.code_display.setPlainText(file_content)

    def compile_code(self) -> None:
        
        start_time = time.time()

        code_text = self.code_display.toPlainText()

        pattern = r'(<<|>>|\#|\[|\]|\,|\;|\:\:|\:|\.|\-\>|\.\.\.|\{|\}|\=|\+\+|\+|\-\-|\-|\*|\/|\%|\=\=|\!\=|\<|\>|\<\=|\>\=|\&\&|\|\||!|&|\||\^|~)|(\d+\.\d+|\d+|\"[^\"]*\")|([a-zA-Z_]\w*)\b'

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
            elif self.integer_pattern.match(token):
                category = 'Número entero'
            elif self.float_pattern.match(token):
                category = 'Número con punto flotante'
            elif self.string_pattern.match(token):
                category = 'Cadena de caracterés'
            else:
                category = 'Identificador'

            token_item = QStandardItem(token)
            category_item = QStandardItem(category)

            model.appendRow([token_item, category_item])
            found_tokens += 1

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        end_time = time.time()

        # Mostramos los logs de los tokens encontrados en el codigo cargado en la gui.

        cursor.insertText(f"Found {found_tokens} tokens in {end_time - start_time:.5f}s" + '\n')

        start_time = time.time()

        code_text = self.code_display.toPlainText()
        
        error_listener = MyErrorListener(self.logs_display)
        
        input_stream = InputStream(code_text)
        lexer = CPP14Lexer(input_stream)
        lexer.removeErrorListeners()
        lexer.addErrorListener(error_listener)
        tokens = CommonTokenStream(lexer)

        tokens = CommonTokenStream(lexer)

        parser = CPP14Parser(tokens)
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        tree = parser.translationUnit()

        """

        dot_content = tree.toStringTree(recog = parser)

        dot_content = re.sub(r'\(\s*([^()]+)\s*\)', r'\1', dot_content)
        dot_content = re.sub(r'(<[^<>]+>)', '', dot_content)  
        dot_content = dot_content.replace(';', '')  

        with open("tree.dot", 'w') as dot_file:
            dot_file.write(dot_content)

        subprocess.call(['dot', '-Tpng', 'tree.dot', '-o', 'tree.png'])

        """

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        end_time = time.time()

        cursor.insertText(f"Finished parsing in {end_time - start_time:.5f}s" + '\n')

class MyErrorListener(ConsoleErrorListener):
    def __init__(self, logs_display):
        self.cursor = logs_display.textCursor()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"Error en línea {line}:{column}: {msg}\n"
        self.cursor.movePosition(QTextCursor.End)
        self.cursor.insertText(error_message)