import sqlite3
import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLineEdit, QPushButton, QLabel
from UI.addEditCoffeeForm import Ui_MainWindow2
from UI.main_UI import Ui_MainWindow


class SecondWindow(QMainWindow, Ui_MainWindow2):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect("data/coffee.sqlite")
        self.cursor = self.connection.cursor()
        self.pushButton.clicked.connect(self.create_entry)
        self.pushButton_2.clicked.connect(self.change_entry)
        self.fill_ComboBoxes(self.comboBox_1, "SELECT name from sorts_coffe")
        self.fill_ComboBoxes(self.comboBox_2, "SELECT degree from roasting")
        self.fill_ComboBoxes(self.comboBox_4, "SELECT value from volumes")

    def fill_ComboBoxes(self, combobox, req):
        res = self.cursor.execute(req).fetchall()
        res = list(map(lambda x: x[0], res))
        combobox.addItems(res)

    def get_id_from_table(self, req):
        return self.cursor.execute(req).fetchone()[0]

    def get_params(self):
        sort_id = self.get_id_from_table("""SELECT ID_SORT
                                                    FROM SORTS_COFFE 
                                                    WHERE NAME = """ + f'"{self.comboBox_1.currentText()}"')
        roasting_id = self.get_id_from_table(f'''SELECT ID_ROASTING
                                                    FROM roasting
                                                    WHERE DEGREE = "{self.comboBox_2.currentText()}"''')
        variable_id = 1 if self.comboBox_3.currentText() == 'молотый' else 2
        volume_id = self.get_id_from_table(f'''SELECT ID_VOLUME
                                                    FROM volumes
                                                    WHERE value = "{self.comboBox_4.currentText()}"''')

        params = f"({sort_id}, {roasting_id}, " \
                 f"{variable_id}, {int(self.lineEdit.text())}, " \
                 f"{volume_id}, '{self.plainTextEdit.toPlainText()}')"
        return params

    def create_entry(self):
        params = self.get_params()
        req = """INSERT INTO coffee (
                       name_sort,
                       roasting_degree,
                       variable,
                       price,
                       volume,
                       description
                   )
                   VALUES """ + params
        self.cursor.execute(req).fetchall()
        self.connection.commit()
        self.close()

    def change_entry(self):
        params = self.get_params()
        params = params[1:len(params) - 1].split(', ')
        req = """UPDATE coffee
                 SET name_sort = """ + f"{params[0]}," + """
                       roasting_degree = """ + f"{params[1]}," + """
                       variable = """ + f"{params[2]}," + """
                       price = """ + f"{params[3]}," + """
                       volume = """ + f"{params[4]}," + """
                       description = """ + f"{params[5]}" + """
                 WHERE id_coffee = """ + f'{self.id}'
        self.cursor.execute(req).fetchall()
        self.connection.commit()
        self.close()

    def displayInfo(self, arg, id=0):
        if arg == 'add':
            self.setWindowTitle('ДОБАВЛЕНИЕ ЗАПИСИ')
            self.pushButton.setVisible(True)
            self.pushButton_2.setVisible(False)
            self.label_7.setVisible(False)
        elif arg == 'change' and id != 0:
            self.setWindowTitle('ИЗМЕНЕНИЕ ЗАПИСИ')
            self.pushButton.setVisible(False)
            self.pushButton_2.setVisible(True)
            self.label_7.setVisible(True)
            self.id = id
            self.label_7.setText(f'Элемент с id = {id}')
        self.show()


class MyWidget(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.buttons = []
        self.connection = sqlite3.connect("data/coffee.sqlite")
        self.cursor = self.connection.cursor()
        self.load_data()
        self.secondWindow = SecondWindow()
        self.button_add.clicked.connect(lambda: self.open_second_form('add'))
        self.button_change.clicked.connect(lambda: self.open_second_form('change'))

    def load_data(self):
        res = self.cursor.execute("select * from coffee").fetchall()
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(['ID', 'Название сорта', 'Степень обжарки', 'Молотый/взернах',
                                                    'Цена', 'Объем упаковки', 'Описание вкуса'])
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(res):
            self.tableWidget.setRowCount(
                self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(str(elem)))

    def closeEvent(self, event):
        self.connection.close()

    def open_second_form(self, arg):
        if arg == 'change':
            row = self.tableWidget.selectedItems()[0].row()
            id = self.tableWidget.item(row, 0).text()
        else:
            id = 0
        self.secondWindow.displayInfo(arg, id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
