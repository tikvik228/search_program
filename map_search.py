import sys
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
import requests
import os


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('search.ui', self)
        self.api_server = "https://static-maps.yandex.ru/1.x/"
        self.api_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"
        self.map_zoom = 8
        self.delta = 0.1
        self.map_ll = [-77.055993, 38.871001]
        self.map_l = 'map'
        self.theme = 'light'
        self.change_theme.clicked.connect(self.change_map_theme)
        self.find.clicked.connect(self.find_point)
        self.gibrid.clicked.connect(self.set_gybrid)
        self.sputnik.clicked.connect(self.set_sat)
        self.scheme.clicked.connect(self.set_j_map)
        self.refresh_map()

    def find_point(self):
        pass
    def change_map_theme(self):
        if self.theme == 'light':
            self.theme = 'dark'
        else:
            self.theme = 'light'
        self.refresh_map()

    def set_sat(self):
        self.map_l = 'admin'
        self.refresh_map()

    def set_gybrid(self):
        self.map_l = 'driving'
        self.refresh_map()

    def set_j_map(self):
        self.map_l = 'map'
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp and self.map_zoom < 21:
            self.map_zoom += 1
        if event.key() == Qt.Key.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        if event.key() == Qt.Key.Key_A:
            self.map_ll[0] -= 0.001
        if event.key() == Qt.Key.Key_D:
            self.map_ll[0] += 0.001
        if event.key() == Qt.Key.Key_S:
            self.map_ll[1] -= 0.001
        if event.key() == Qt.Key.Key_W:
            self.map_ll[1] += 0.001
        self.refresh_map()

    def refresh_map(self):
        map_params = {"ll": ','.join(map(str, self.map_ll)),
                      "l": self.map_l,
                      "z": self.map_zoom,
                      "theme": self.theme,
                      "apikey": self.api_key}

        response = requests.get(self.api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса")
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.map_label.setPixmap(pixmap)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())