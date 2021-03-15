import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, \
    QPushButton
from PyQt5.QtWidgets import QMainWindow

# имена полей, используемых баз данных
HEADERS = {'fuel_coefficients': ['id', 'value', 'coefficients'],
           'equipment': ['id', 'aircraft_id', 'type', 'number', 'max_number_of_seats'],
           'summer_winter_coefficients': ['id', 'aircraft_id', 'number', 'summer_coefficient', 'winter_coefficient']
           }


# дополнительная форма, в которой производятся изменения таблиц
class SecondForm(QWidget):
    def __init__(self, creator):
        super().__init__()

        self.creator = creator
        self.mode = True

        self.setWindowTitle(f'Добавляем запись в {creator.comboBox.currentText()}')

        self.main_layout = QVBoxLayout(self)

        self.number_of_inputs = len(HEADERS[creator.comboBox.currentText()])
        self.hbox_layouts = []
        self.labels = []
        self.inputs = []

        self.add_change_bttn = QPushButton(self)
        self.add_change_bttn.setText('Добавить')
        self.add_change_bttn.clicked.connect(self.add_change)
        self.main_layout.addWidget(self.add_change_bttn)
        self.result = []

        self.setLayout(self.main_layout)

    # обработчик нажатия на клавиши "добавить и изменить"
    def add_change(self):
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        table_name = self.creator.comboBox.currentText()
        self.number_of_inputs = len(HEADERS[self.creator.comboBox.currentText()])
        if self.mode:
            request = f'INSERT INTO {table_name} (' + \
                      ', '.join(HEADERS[table_name]) + \
                      ') VALUES ( ' + \
                      ', '.join([i.text() for i in self.inputs]) + \
                      ')'
            cur.execute(request).fetchall()
        else:
            request = f'UPDATE {table_name} SET ' + \
                      ', '.join([f'{HEADERS[table_name][i]} = {self.inputs[i].text()}'
                                 for i in range(1, self.number_of_inputs)]) + ' WHERE ' + \
                      f'id = {self.inputs[0].text()}' + ';'
            cur.execute(request).fetchall()

        con.commit()
        con.close()
        self.creator.update_table()
        self.close()

    # функция очистки формы
    def clear_form(self):
        for i in self.labels:
            i.deleteLater()
        self.labels = []
        for i in self.inputs:
            i.deleteLater()
        self.inputs = []
        for i in self.hbox_layouts:
            self.main_layout.removeItem(i)
            i.deleteLater()
        self.hbox_layouts = []

    # функция для построения формы в зависимости от изменяемой таблицы
    def add_widgets(self):
        self.number_of_inputs = len(HEADERS[self.creator.comboBox.currentText()])
        for i in range(self.number_of_inputs):
            self.hbox_layouts.append(QHBoxLayout(self))
            self.labels.append(QLabel(self))
            self.labels[-1].setText(HEADERS[self.creator.comboBox.currentText()][i])
            self.hbox_layouts[-1].addWidget(self.labels[-1])
            self.inputs.append(QLineEdit(self))
            self.hbox_layouts[-1].addWidget(self.inputs[-1])
            self.main_layout.addLayout(self.hbox_layouts[-1])
            if not self.mode:
                row = self.creator.tableWidget.currentRow()
                self.inputs[-1].setText(self.creator.tableWidget.item(row, i).text())
                if i == 0:
                    self.inputs[-1].setEnabled(False)
        if self.mode:
            self.setWindowTitle(f'Добавляем запись в {self.creator.comboBox.currentText()}')
            self.add_change_bttn.setText('Добавить')
        else:
            self.setWindowTitle(f'Изменяем запись из {self.creator.comboBox.currentText()}')
            self.add_change_bttn.setText('Изменить')


# основная форма изменения коэффициентов
class CoefficientEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("coefficient_form.ui", self)
        self.pushButton.clicked.connect(self.add_record)

        self.pushButton_2.clicked.connect(self.edit_record)

        self.pushButton_3.clicked.connect(self.delete_record)

        self.comboBox.addItems(HEADERS.keys())
        self.comboBox.currentIndexChanged.connect(self.update_table)

        self.second_form = SecondForm(self)
        self.result = []
        self.update_table()

    # обработчик кнопки добавления записи
    def add_record(self):
        self.second_form.mode = True
        self.second_form.clear_form()
        self.second_form.add_widgets()
        self.second_form.show()

    # обработчик кнопки изменения записи
    def edit_record(self):
        if self.tableWidget.currentRow() != -1:
            self.second_form.mode = False
            self.second_form.clear_form()
            self.second_form.add_widgets()
            self.second_form.show()

    # обработчик кнопки удаления записи
    def delete_record(self):
        if self.tableWidget.currentRow() != -1:
            con = sqlite3.connect('coefficients.sqlite')
            cur = con.cursor()
            table_name = self.comboBox.currentText()
            row = self.tableWidget.currentRow()
            request = f'DELETE FROM {table_name} ' + \
                      f'WHERE id = {self.tableWidget.item(row, 0).text()}'
            cur.execute(request).fetchall()
            con.commit()
            con.close()
            self.update_table()

    # вспомогательная функция, для обновления таблицы после внесенных изменений
    def update_table(self):
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.result = cur.execute(f"""SELECT * from {self.comboBox.currentText()};""").fetchall()

        self.tableWidget.setRowCount(len(self.result))
        self.tableWidget.setColumnCount(len(self.result[0]))

        self.tableWidget.setHorizontalHeaderLabels(HEADERS[self.comboBox.currentText()])
        for i, elem in enumerate(self.result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        con.close()
