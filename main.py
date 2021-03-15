import datetime as dt
import sqlite3
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTableWidgetItem

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


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main_form.ui", self)
        self.ft = 'DP-194'
        self.at = 'A320-213'
        self.result = []
        self.curr_seats = []
        self.curr_cargo = []
        self.current_aircraft_id = -1
        self.fuel_index = -1
        self.trip_fuel_index = -1
        self.pax_index = 0
        self.cargo_index = 0
        self.season = 'spring summer'
        self.ft = 'SU1065'
        self.at = 'A320-214'
        self.pax_weight, self.cargo_weight, self.ZFV, self.LIZFW, self.MACZEW = 0, 0, 0, 0, 0
        self.TOF, self.TOW, self.LITOW, self.MACTOW, self.trip_fuel = 0, 0, 0, 0, 0
        self.Landing_W, self.LILAW, self.MACLAW = 0, 0, 0

        self.coefficient_editor_form = CoefficientEditor()

        self.change_coeff_bttn.clicked.connect(self.coefficient_editor_form.show)

        self.dateEdit.setDate(dt.datetime.now().date())

        self.timeEdit.setTime(dt.datetime.now().time())

        self.Flight.currentIndexChanged.connect(self.on_flight_change)

        self.aircraft_type.currentIndexChanged.connect(self.on_aircraft_type_change)

        self.aircraft_reg_num.currentIndexChanged.connect(self.on_reg_num_change)

        self.seatstableWidget.cellChanged.connect(self.seats_cell_changed)

        self.cargotableWidget.cellChanged.connect(self.cargo_cell_changed)

        self.checkbutton.clicked.connect(self.check)

        self.save_bttn.clicked.connect(self.save_resoults)

        self.update_flight_list()
        self.errors.setText('')

    # метод обновляет выпадающий список рейсов
    def update_flight_list(self):
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.result = cur.execute('select DISTINCT value from aircraft_info where field = "Flight"').fetchall()

        self.Flight.clear()
        self.Flight.addItems([i[0] for i in self.result])

        con.close()

    # метод обновляет выпадающий список типов воздушных судов в зависимости от выбранного рейса
    def on_flight_change(self):
        self.ft = self.Flight.currentText()
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.result = cur.execute(f'''SELECT DISTINCT value
                                          FROM aircraft_info
                                         WHERE aircraft_id IN (
                                                                 SELECT aircraft_id
                                                                   FROM aircraft_info
                                                                  WHERE field = 'Flight' AND 
                                                                        value = '{self.ft}'
                                                             )
                                        AND 
                                               field = 'aircraft_model';''').fetchall()

        self.aircraft_type.clear()
        self.aircraft_type.addItems([i[0] for i in self.result])

        con.close()

    # метод обновляет выпадающий список бортов в зависимости от выбранных рейса и типа воздушного судна
    def on_aircraft_type_change(self):
        if self.aircraft_type.currentText() == '':
            return
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.at = self.aircraft_type.currentText()
        self.result = cur.execute(f'''SELECT value
                                          FROM aircraft_info
                                         WHERE aircraft_id IN (
                                                   SELECT DISTINCT aircraft_id
                                                     FROM aircraft_info
                                                    WHERE aircraft_id IN (
                                                              SELECT aircraft_id
                                                                FROM aircraft_info
                                                               WHERE field = 'Flight' AND 
                                                                     value = '{self.ft}'
                                                          )
                                        AND 
                                                          field = 'aircraft_model' AND 
                                                          value = '{self.at}'
                                               )
                                        AND 
                                               field = 'aircraft_tn';
                                        ''').fetchall()
        self.aircraft_reg_num.clear()
        self.aircraft_reg_num.addItems([i[0] for i in self.result])

        con.close()

    # метод заполняет информацию о выбранном воздушном судне в соответствующих полях формы
    def on_reg_num_change(self):
        if self.aircraft_reg_num.currentText() == '':
            return
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()

        self.result = cur.execute(f'''SELECT *
                                        FROM aircraft_info
                                        WHERE aircraft_id IN (
                                                        SELECT aircraft_id
                                                          FROM aircraft_info
                                                         WHERE value = '{self.aircraft_reg_num.currentText()}' AND
                                                                field = 'aircraft_tn');''').fetchall()

        con.close()
        for i in self.result:
            if i[2] == 'Qrew':
                self.Aircraft_qrew.setText(i[3])
            elif i[2] == 'seats_conf':
                self.seats_complectation.setText(i[3])
            elif i[2] == 'DOW':
                self.DOW.setText(str(i[3]))
            elif i[2] == 'DOI':
                self.DOI.setText(str(i[3]))
        self.current_aircraft_id = self.result[0][1]
        self.load_seats()

    # метод загружается комплектацию выбранного воздушного судна (кресла и багажные отсеки)
    def load_seats(self):
        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.result = cur.execute(f"""SELECT number,
                                               type,
                                               max_number_of_seats
                                          FROM equipment
                                         WHERE aircraft_id = '{self.current_aircraft_id}'
                                         ORDER BY number;""").fetchall()

        self.curr_seats = [(i[1], i[2]) for i in self.result if i[1] != 'cargo']
        self.curr_cargo = [(i[0], i[2]) for i in self.result if i[1] == 'cargo']

        self.seatstableWidget.clear()
        self.seatstableWidget.setRowCount(3)
        self.seatstableWidget.setColumnCount(len(self.curr_seats))
        self.seatstableWidget.setVerticalHeaderLabels(('type', 'max_of_seats', 'people'))

        for i, elem in enumerate(self.curr_seats):
            for j, val in enumerate(elem):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)
                self.seatstableWidget.setItem(j, i, item)
            self.seatstableWidget.setItem(2, i, QTableWidgetItem(str(0)))

        self.cargotableWidget.clear()
        self.cargotableWidget.setRowCount(3)
        self.cargotableWidget.setColumnCount(len(self.curr_cargo))
        self.cargotableWidget.setVerticalHeaderLabels(('type', 'max_of_cargo', 'cargo'))

        for i, elem in enumerate(self.curr_cargo):
            for j, val in enumerate(elem):
                item = QTableWidgetItem(str(val))
                item.setFlags(Qt.ItemIsEnabled)
                self.cargotableWidget.setItem(j, i, item)
            self.cargotableWidget.setItem(2, i, QTableWidgetItem(str(0)))

        con.close()

    # функция проверки корректности введенного значения количества массажиров на конкретном ряду
    def seats_cell_changed(self, c_row, c_column):
        if c_row != 2:
            return
        if not self.seatstableWidget.item(c_row, c_column).text().isdigit():
            item = QTableWidgetItem('0')
            self.seatstableWidget.setItem(c_row, c_column, item)
            self.errors.setText(f'ошибка ввода, seats {c_column + 1}, поддерживаются только числа')
        elif int(self.seatstableWidget.item(c_row, c_column).text()) > \
                int(self.seatstableWidget.item(c_row - 1, c_column).text()):
            item = QTableWidgetItem('0')
            self.seatstableWidget.setItem(c_row, c_column, item)
            self.errors.setText(f'ошибка ввода, seats {c_column + 1}, больше максимального значения')

    # функция проверки корректности введенного значения количества багажа в конкретном багажном отсеке
    def cargo_cell_changed(self, c_row, c_column):
        if c_row != 2:
            return
        if not self.cargotableWidget.item(c_row, c_column).text().isdigit():
            item = QTableWidgetItem('0')
            self.cargotableWidget.setItem(c_row, c_column, item)
            self.errors.setText(f'ошибка ввода, cargo {c_column + 1}, поддерживаются только числа')
        elif int(self.cargotableWidget.item(c_row, c_column).text()) > \
                int(self.cargotableWidget.item(c_row - 1, c_column).text()):
            item = QTableWidgetItem('0')
            self.cargotableWidget.setItem(c_row, c_column, item)
            self.errors.setText(f'ошибка ввода, seats {c_column + 1}, больше максимального значения')

    # функция общей проверки корректности заполнения
    def check(self):
        count = len(self.curr_seats)
        curr_seats = sum([int(self.seatstableWidget.item(2, i).text()) for i in range(count)])
        if curr_seats > self.PaxSpinBox.value():
            self.errors.setText('ошибка ввода, seats, сумма больше максимального значения')
            self.seats_ok.setText('seats error')
            return
        elif curr_seats < self.PaxSpinBox.value():
            self.errors.setText('ошибка ввода, seats, сумма больше минимального значения')
            self.seats_ok.setText('seats error')
            return
        self.seats_ok.setText('ok')

        count = len(self.curr_cargo)
        curr_cargo = sum([int(self.cargotableWidget.item(2, i).text()) for i in range(count)])
        if curr_cargo > self.CargoSpinBox.value():
            self.errors.setText('ошибка ввода, cargo, сумма больше максимального значения')
            self.cargo_ok.setText('cargo error')
            return
        elif curr_cargo < self.CargoSpinBox.value():
            self.errors.setText('ошибка ввода, cargo, сумма больше минимального значения')
            self.cargo_ok.setText('cargo error')
            return
        self.cargo_ok.setText('ok')

        con = sqlite3.connect('coefficients.sqlite')
        cur = con.cursor()
        self.result = cur.execute(f"""SELECT number,
                                                       summer_coefficient,
                                                       winter_coefficient
                                                  FROM summer_winter_coefficients
                                                 WHERE aircraft_id = '{self.current_aircraft_id}'
                                                 ORDER BY number;""").fetchall()

        if 2 < int(self.dateEdit.dateTime().toString('MM')) < 9:
            self.season = 'spring summer'
        else:
            self.season = 'autumn winter'

        self.pax_index = 0
        for i in range(len(self.curr_seats)):
            if self.season == 'spring summer':
                self.pax_index += int(self.seatstableWidget.item(2, i).text()) * float(self.result[i][1])
            elif self.season == 'autumn winter':
                self.pax_index += int(self.seatstableWidget.item(2, i).text()) * float(self.result[i][2])

        self.result = cur.execute(f"""SELECT number,
                                                               coefficient
                                                          FROM cargo_coefficients
                                                         WHERE aircraft_id = '{self.current_aircraft_id}'
                                                         ORDER BY number;""").fetchall()

        self.cargo_index = 0
        for i in range(len(self.curr_cargo)):
            self.cargo_index += int(self.cargotableWidget.item(2, i).text()) * float(self.result[i][1])

        self.result = cur.execute(f"""SELECT value,
                                                                       coefficients
                                                                  FROM fuel_coefficients
                                                                 ORDER BY value;""").fetchall()
        con.close()
        curr = 0.85
        for i in self.result:
            if i[0] >= self.FuelSpinBox.value():
                self.fuel_index = (i[1] + curr) / 2
                break
            curr = i[1]

        curr = 0.85
        for i in self.result:
            if i[0] >= self.TripFuelSpinBox.value():
                self.trip_fuel_index = (i[1] + curr) / 2
                break
            curr = i[1]

        self.seats_count = dict()

        for index, i in enumerate(self.curr_seats):
            if i[0] in self.seats_count.keys():
                self.seats_count[i[0]] += int(self.seatstableWidget.item(2, index).text())
            else:
                self.seats_count[i[0]] = int(self.seatstableWidget.item(2, index).text())

        self.pax_weight = 85 * self.PaxSpinBox.value()
        self.cargo_weight = self.CargoSpinBox.value()
        self.ZFV = int(self.DOW.text()) + self.pax_weight + self.cargo_weight
        self.LIZFW = round(self.pax_index + self.cargo_index + float(self.DOI.text()), 2)
        self.MACZEW = round(25.036 + (23843.6 / self.ZFV) * (self.LIZFW - 50), 2)
        self.TOF = self.FuelSpinBox.value()
        self.TOW = self.ZFV + self.TOF
        self.LITOW = round(self.fuel_index + self.LIZFW, 2)
        self.MACTOW = round(25.036 + (23543.6 / self.TOW) * (self.LITOW - 50), 2)
        self.trip_fuel = self.TripFuelSpinBox.value()
        self.Landing_W = self.TOW - self.trip_fuel
        self.LILAW = round(self.LIZFW + self.trip_fuel_index, 2)
        self.MACLAW = round(25.036 + (23543.6 / self.Landing_W) * (self.LILAW - 50), 2)

        if not (27 < self.MACZEW < 30):
            self.errors.setText(f'внимание! превышение индекса без топлива {self.MACZEW}')
            return
        elif not (27 < self.MACTOW < 30):
            self.errors.setText(f'угроза! превышение индекса на вылет {self.MACTOW}')
            return

        if len(self.DispatcherName.text()) == 0:
            self.errors.setText('поле "диспетчер" не заполнено')
            return

        if not (27 < self.MACLAW < 30):
            self.errors.setText(f'внимание! превышение индекса на посадке {self.MACLAW}')
        else:
            self.errors.setText('ok')

        self.LastCheckStatus.setText('ok')
        self.resoults.setText(f'MACLAW = {round(self.MACLAW, 2)}\t' +
                              f'MACZFW = {round(self.MACZEW, 2)}\t' +
                              f'MACTOW = {round(self.MACTOW)}')

    # метод, записывающий результат в файл
    def save_resoults(self):
        with open('output.txt', 'w') as f:
            f.write(f'\t\t {self.dateEdit.dateTime().toString("DDMMyyyy")}\n')
            f.write(f'\t\t {self.aircraft_type.currentText()}\n')
            f.write('L O A D S H E E T \t \t \t CHECKED BY        APPROVED       EDNO\n')
            f.write(f'ALL WEIGHTS IN KG \t \t \t \t {self.DispatcherName.text()}\n')
            f.write(' FLIGHT \t \t A/C REG  VERSION \t \t \t crew \t date \t \t time\n')
            f.write(f'{self.Flight.currentText()}\t \t \t {self.aircraft_reg_num.currentText()}' +
                    f' \t \t{self.seats_complectation.text()} \t \t \t {self.Aircraft_qrew.text()}' +
                    f' \t  {self.dateEdit.dateTime().toString("ddMMyyyy")} \t' +
                    f'{self.timeEdit.time().toString("hhmm")}\n')
            f.write('\t \t \t \t \t WEIGHT\n')
            f.write(f'LOAD  IN  COMPARTMENTS {self.cargo_weight}\n')
            f.write(f'PASSENGER / CABIN  BAG {self.pax_weight} \t {self.PaxSpinBox.value()}\n')
            f.write(f'TOTAL TRAFFIC LOAD {self.pax_weight + self.PaxSpinBox.value()}\n')
            f.write(f'DRY OPERATING WEIGHT {int(self.DOW.text())}\n')
            f.write(f'ZERO FUEL WEIGHT ACTUAL {self.ZFV}\n')
            f.write(' -------------------------------\n')
            f.write(f'TAKE OFF FUEL {self.TOF}\n')
            f.write(f'TAKE OFF FUEL WEIGHT {self.TOW}\n')
            f.write(' -------------------------------\n')
            f.write(f'TRIP FUEL {self.TripFuelSpinBox.value()}\n')
            f.write(f'LANDING WEIGHT ACTUAL {self.Landing_W}\n')
            f.write(' -------------------------------\n')
            f.write('BALANCE AND SEATING CONDITIONS\n')
            f.write(f'DOI \t \t {float(self.DOI.text())}\n')
            f.write(f'LIZFW \t \t {self.LIZFW} \t MACZEW \t \t {self.MACZEW}\n')
            f.write(f'LITOW \t \t {self.LITOW} \t MACTOW \t \t {self.MACTOW}\n')
            f.write(f'LILAW \t \t {self.LILAW} \t MACLAW \t \t {self.MACLAW}\n\n')
            f.write('BALANCE AND SEATING CONDITIONS\n')
            f.write('SEATING\n')
            f.write('\t'.join([f'{i}\\{self.seats_count[i]}' for i in self.seats_count.keys()]) + '\n')
            f.write('LOADMESSAGE  AND  CAPTAINS    INFORMATION  BEFORE  LMS\n\n')
            f.write('THIS AIRCRAFT  HAS  BEEN  LOADED  IN  ACCORDANCE  WITH  THE\n')
            f.write('LOADING   INSTRUCTIONS INCLUDING  THE DEVIATIONS  RECORDED\n')
            f.write('THE  LOAD HAS  BEEN SECURED IN ACCORDANCE  WITH COMPANY\n')
            f.write('REGULATIONS\n\n')
            f.write('SIGNED. . . . . . . . . . . . . . . \n\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec())
