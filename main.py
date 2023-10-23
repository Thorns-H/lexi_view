from PyQt5.QtWidgets import QApplication
import sys

sys.path.append('imports/')

from imports.lexical_analysis import *

def main() -> None:
    app = QApplication([])
    window = lexical_analysis()
    screen_geometry = app.desktop().availableGeometry()
    window.setGeometry((screen_geometry.width() - window.width()) // 2, (screen_geometry.height() - window.height()) // 2, window.width(), window.height())
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()