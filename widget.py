import webbrowser

from data_parser import DataParser
from script_caller import ScriptCaller

from PySide6 import QtWidgets
from PySide6.QtWidgets import QLabel, QSpinBox, QComboBox, QCheckBox


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.combobox_duration = None
        self.combobox_speed = None
        self.input_speed = None
        self.combobox_choose_days = None
        self.open_file_checkbox = None
        self.checkbox_layout = None
        self.input_duration = None
        self.script_caller = ScriptCaller()
        self.data_parser = DataParser("./simulated_traffic_script+json/10.json")
        self.layout = QtWidgets.QVBoxLayout(self)
        self.populate()

    def populate(self):
        self.create_choose_day()
        self.create_choose_speed()
        self.create_choose_display_duration()
        self.create_open_file_checkbox()

        # button leitet einträge weiter und lädt farbbalken
        confirm_button = QtWidgets.QPushButton("Bestätigen", self)
        confirm_button.clicked.connect(self.clear_contents)
        self.layout.addWidget(confirm_button)

    def populate_after_1st_time(self):
        # deletes back btn
        # index keeps changing so loop necessary
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.populate()

    def create_choose_day(self):
        number_days = self.data_parser.get_number_of_days()
        choose_days_label = QLabel("Tag wählen")
        choose_days_label.setFixedSize(200, 30)
        self.layout.addWidget(choose_days_label)
        self.combobox_choose_days = QComboBox()

        for day_counter in range(number_days):
            self.combobox_choose_days.addItem(str(day_counter + 1))

        self.combobox_choose_days.setFixedSize(100, 30)
        self.layout.addWidget(self.combobox_choose_days)

    def create_choose_speed(self):
        speed_label = QLabel("Fortschrittsgeschwingkeit eingeben")
        speed_label.setFixedSize(200, 30)
        self.layout.addWidget(speed_label)

        self.input_speed = QSpinBox()
        self.input_speed.setMinimum(1)
        self.input_speed.setFixedSize(100, 30)
        self.layout.addWidget(self.input_speed)

        self.combobox_speed = QComboBox()
        self.combobox_speed.addItem("Minuten")
        self.combobox_speed.addItem("Stunden")
        self.combobox_speed.setFixedSize(100, 30)
        self.layout.addWidget(self.combobox_speed)

    def create_choose_display_duration(self):
        duration_label = QLabel("Darstellungsdauer eingeben")
        duration_label.setFixedSize(200, 30)
        self.layout.addWidget(duration_label)

        self.input_duration = QSpinBox()
        self.input_duration.setMinimum(1)
        self.input_duration.setFixedSize(100, 30)
        self.layout.addWidget(self.input_duration)

        self.combobox_duration = QComboBox()
        self.combobox_duration.addItem("Minuten")
        self.combobox_duration.addItem("Stunden")
        self.combobox_duration.setFixedSize(100, 30)
        self.layout.addWidget(self.combobox_duration)

    def create_open_file_checkbox(self):
        self.checkbox_layout = QtWidgets.QHBoxLayout(self)

        open_file_label = QLabel("Datei automatisch öffnen?")
        open_file_label.setFixedSize(200, 30)
        self.checkbox_layout.addWidget(open_file_label)

        self.open_file_checkbox = QCheckBox()
        self.open_file_checkbox.setChecked(False)
        self.checkbox_layout.addWidget(self.open_file_checkbox)

        self.layout.addLayout(self.checkbox_layout)

    def get_input(self):
        return [self.combobox_choose_days.currentText(),
                str(self.input_speed.value()), self.combobox_speed.currentText(),
                str(self.input_duration.value()), self.combobox_duration.currentText()]

    def clear_contents(self):
        self.get_input()
        self.script_caller.start_script(self.get_input())
        if self.open_file_checkbox.isChecked():
            webbrowser.open("marker.html")
        # Clear all child widgets from layout
        for i in reversed(range(self.layout.count())):
            widget = self.layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        # clears all child widgets fron checkbox_layout
        for i in reversed(range(self.checkbox_layout.count())):
            widget = self.checkbox_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        back_btn = QtWidgets.QPushButton("zurück", self)
        back_btn.clicked.connect(self.populate_after_1st_time)
        self.layout.addWidget(back_btn)
