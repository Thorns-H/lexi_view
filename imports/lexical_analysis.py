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

def format_variables(variables: tuple) -> dict:

    dictionary = {}

    for variable in variables:
        if len(variable) >= 2:
            identifier = variable[1]
            value = [variable[2]]
            if identifier in dictionary:
                dictionary[identifier].extend(value)
            else:
                dictionary[identifier] = value

    return dictionary

def find_variable_references(variable_name, cpp_code) -> list:
    regular_expression = rf'\b{re.escape(variable_name)}\b'
    matches = re.finditer(regular_expression, cpp_code)
    
    referenced_lines = []

    for match in matches:
        start = match.start()
        line_number = cpp_code.count('\n', 0, start) + 1
        referenced_lines.append(line_number)

    return referenced_lines

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

# Clase secundaria para los tokens.
class Identifier:
    def __init__(self, text, line, column, data_type):
        self.text = text
        self.line = line
        self.column = column
        self.data_type = data_type

    def __str__(self) -> str:
        return f"Identifier: {self.text}, Line: {self.line}:{self.column}, Type: {self.data_type}"
    
    def is_numeric(self) -> bool:
        if self.data_type in ['int', 'float']:
            return True
        else:
            return False

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
        self.search_button.clicked.connect(self.search_variable)

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
        variable_pattern = r'\s*(\w+)\s+(\w+)\s*(?:=\s*([^;]+))?;\s*'

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

        input_stream = InputStream(code_text)
        lexer = CPP14Lexer(input_stream)
        tokens_track = lexer.getAllTokens()

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        end_time = time.time()

        cursor.insertText(f"Finished parsing in {end_time - start_time:.5f}s" + '\n')

        start_time = time.time()

        custom_identifiers = []

        for i in range(0, len(tokens_track)):
            current_token = tokens_track[i]
            
            if current_token.text in ['int', 'float', 'string', 'char', 'bool']:
                next_token = tokens_track[i + 1]
                
                identifier = Identifier(
                    text = next_token.text,
                    line = next_token.line,
                    column = next_token.column,
                    data_type = current_token.text
                )
                
                custom_identifiers.append(identifier)

        assign_pattern = re.compile(r'(\w+)\s*=\s*(\d+|\d*\.\d+|".+?")')
        matches = assign_pattern.finditer(code_text)

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        for match in matches:
            identifier_name = match.group(1)
            value = match.group(2)

            matching_identifiers = [identifier for identifier in custom_identifiers if identifier.text == identifier_name]

            if matching_identifiers:
                identifier = matching_identifiers[0]

                if identifier.is_numeric():
                    if not (value.isdigit() or (value.count('.') == 1 and value.replace('.', '').isdigit())):
                        cursor.insertText(f"Error at line {identifier.line}:{identifier.column}, '{identifier.text}' value must be of type '{identifier.data_type}'")
                else:
                    if not (value.startswith('"') and value.endswith('"')):
                        cursor.insertText(f"Error at line {identifier.line}:{identifier.column}, '{identifier.text}' value must be of type '{identifier.data_type}'")

        # Expresión regular para buscar operaciones de la forma 'identifier.text operador operand;'
        operation_pattern = re.compile(r'(\b\w+\b)\s*([\+\-\*/])\s*(\w+|\d+);')

        # Busca todas las coincidencias en el texto
        matches = operation_pattern.finditer(code_text)

        # Verifica la validez de las operaciones
        for match in matches:
            operand1 = match.group(1)
            operator = match.group(2)
            operand2 = match.group(3)

            # Verifica la validez de la operación según tus reglas semánticas
            matching_identifiers = [identifier for identifier in custom_identifiers if identifier.text == operand1]

            if matching_identifiers:
                # La operación es válida si ambos operandos tienen el mismo tipo de datos
                identifier = matching_identifiers[0]
                if isinstance(operand2, str) and operand2.isnumeric() and identifier.is_numeric():
                    cursor.insertText(f"Operación válida: {operand1} {operator} {operand2}\n")
                elif isinstance(operand2, str) and operand2.startswith('"') and operand2.endswith('"') and not identifier.is_numeric():
                    cursor.insertText(f"Operación válida: {operand1} {operator} {operand2}\n")
                else:
                    cursor.insertText(f"Error cannot perform operation {operand1} {operator} {operand2}\n")

        end_time = time.time()

        cursor.insertText(f"Finished verifications in {end_time - start_time:.5f}s" + '\n')

    def search_variable(self) -> None:

        variable_name = self.input.text()

        start_time = time.time()

        code_text = self.code_display.toPlainText()

        variable_pattern = r'\s*(\w+)\s+(\w+)\s*(?:=\s*([^;]+))?;\s*'

        variables = re.findall(variable_pattern, code_text)
        variables = format_variables(variables)

        cursor = self.variable_logs.textCursor()
        cursor.movePosition(QTextCursor.End)

        if variable_name in variables:
            cursor.insertText(f'{variable_name} : {variables[variable_name]}' + '\n')
        else:
            cursor.insertText(f'Variable {variable_name} not found.' + '\n')

        end_time = time.time()

        cursor = self.logs_display.textCursor()
        cursor.movePosition(QTextCursor.End)

        cursor.insertText(f"Finished variable search in {end_time - start_time:.5f}s" + '\n')
class MyErrorListener(ConsoleErrorListener):
    def __init__(self, logs_display):
        self.cursor = logs_display.textCursor()

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        error_message = f"Error at line {line}:{column}: {msg}\n"
        self.cursor.movePosition(QTextCursor.End)
        self.cursor.insertText(error_message)