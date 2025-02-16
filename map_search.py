import sys
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QRadioButton
import requests


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('search.ui', self)
        self.api_server = "https://static-maps.yandex.ru/v1"
        self.api_key = "f3a0fe3a-b07e-4840-a1da-06f18b2ddf13"

        self.geocoder_server = 'http://geocode-maps.yandex.ru/1.x/?'
        self.geocoder_key = '8013b162-6b42-4997-9691-77b7074026e0'

        self.map_zoom = 8
        self.delta = 0.1
        self.map_ll = [-77.055993, 38.871001]
        self.map_l = 'map'
        self.theme = 'light'
        self.point_marker = []
        self.point_address = ""
        self.point_postal_index = ""
        self.full_address = ""
        self.change_theme.clicked.connect(self.change_map_theme)
        self.find.clicked.connect(self.find_point)
        self.transport_button.clicked.connect(self.set_transport)
        self.admin_button.clicked.connect(self.set_admin)
        self.standart_button.clicked.connect(self.set_standart)
        self.clear_result.clicked.connect(self.clear_point)
        self.postal_checkbox.stateChanged.connect(self.postal_operator)
        self.postal_checkbox.setEnabled(False)
        self.refresh_map()

    def clear_point(self):
        self.point_address = ""
        self.point_postal_index = ""
        self.full_address = ""
        self.point_marker.clear()
        self.postal_checkbox.setEnabled(False)
        self.refresh_map()


    def find_point(self):
        geocode = self.lineEdit.text()
        try:
            geocoder_request = f'{self.geocoder_server}apikey={self.geocoder_key}&geocode={geocode}&format=json'
            response = requests.get(geocoder_request)
            # Выполняем запрос.
            if response:
                json_response = response.json()

                toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
                # Полный адрес топонима:
                self.point_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
                # Координаты центра топонима:
                self.map_ll = list(map(float, toponym["Point"]["pos"].split()))
                # почтовый индекс
                try:
                    self.point_postal_index = toponym["metaDataProperty"]["GeocoderMetaData"]["Address"]["postal_code"]
                    self.postal_checkbox.setEnabled(True)
                except KeyError as k:
                    self.statusBar().showMessage("почтовый индекс объекта не найден", 20000)
                    self.point_postal_index = ""
                    self.postal_checkbox.setChecked(False)
                    self.postal_checkbox.setEnabled(False)

                self.point_marker = self.map_ll.copy()
                self.postal_operator()
            else:
                self.statusBar().showMessage(f"Ошибка выполнения запроса -\n"
                                             f"Http статус: {response.status_code} ({response.reason})", 20000)

        except ValueError as v:
            self.statusBar().showMessage(v.__class__.__name__ + " : ошибка перевода запроса в json", 20000)
        except IndexError as a:
            self.statusBar().showMessage(a.__class__.__name__ + ": объектов с таким адресом не найдено", 20000)
        self.refresh_map()

    def postal_operator(self):
        if self.postal_checkbox.isChecked():
            self.full_address = self.point_address + ", п. индекс: " + self.point_postal_index
        else:
            self.full_address = self.point_address
        self.refresh_map()

    def change_map_theme(self):
        if self.theme == 'light':
            self.theme = 'dark'
        else:
            self.theme = 'light'
        self.refresh_map()

    def set_admin(self):
        self.map_l = 'admin'
        self.refresh_map()

    def set_transport(self):
        self.map_l = 'driving'
        self.refresh_map()

    def set_standart(self):
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
                      "z": self.map_zoom,
                      "theme": self.theme,
                      "maptype": self.map_l,
                      "lang": "ru_RU",
                      "pt": ','.join(map(str, self.point_marker)),
                      "apikey": self.api_key}

        response = requests.get(self.api_server, params=map_params)
        if not response:
            print("Ошибка выполнения запроса")
            print("URL:", response.url, "Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        self.map_label.setPixmap(pixmap)
        self.show_res_line.setText(self.full_address)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())