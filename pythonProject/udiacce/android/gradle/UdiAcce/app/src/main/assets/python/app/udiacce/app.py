"""
Our first accelerometer
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from rubicon.java import JavaClass

MainActivity = JavaClass('org/beeware/android/MainActivity')


class UdiAcce(toga.App):

    def __init__(self):
        super().__init__()
        self.main_window = toga.MainWindow(title=self.formal_name)

    def startup(self):
        main_box = toga.Box(style=Pack(direction=COLUMN))

        get_data_label = toga.Label(
            'Do You Want Your Accelerometer\'s Data ?',
            style=Pack(padding=(0, 5))
        )

        get_data_button = toga.Button(
            'I want it NOW!',
            on_press=self.get_acce_data,
            style=Pack(padding=5)
        )
        main_box.add(get_data_label)
        main_box.add(get_data_button)

        self.main_window.content = main_box
        self.main_window.show()

    def get_acce_data(self, widget):
        try:
            events = MainActivity.getEvents()
            events = events.split()
            # display data
            data_label = toga.Label(
                "Accelerometer's data as: [x, y, z]",
                style=Pack(padding=(0, 5))
            )
            data_box = toga.Box(style=Pack(direction=COLUMN, padding=(5, 5)))
            data_box.add(data_label)
            event_box = toga.MultilineTextInput(id='eb', readonly=True, initial=events, placeholder=events,
                                                style=Pack(direction=COLUMN, width=300, height=400))
            data_box.add(event_box)

            # Update events button
            update_events_button = toga.Button(
                'Update Accelerometer\'s Data',
                on_press=self.get_acce_data,
                style=Pack(direction=COLUMN, width=300, padding=(0, 5))
            )

            data_box.add(update_events_button)

            self.main_window.content = data_box
            self.main_window.show()

        except Exception as e:
            self.main_window.info_dialog(
                'Accelerometer\'s Data: ',
                "No data found due to error: {}".format(e)
            )


def main():
    return UdiAcce()
