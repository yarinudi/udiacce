import asyncio

from rubicon.java import android_events
from toga.handlers import wrapped_handler

from .libs.activity import IPythonApp, MainActivity
from .window import Window


# `MainWindow` is defined here in `app.py`, not `window.py`, to mollify the test suite.
class MainWindow(Window):
    pass


class TogaApp(IPythonApp):
    last_intent_requestcode = -1  # always increment before using it for invoking new Intents
    running_intents = {}          # dictionary for currently running Intents

    def __init__(self, app):
        super().__init__()
        self._interface = app
        MainActivity.setPythonApp(self)
        print('Python app launched & stored in Android Activity class')

    def onCreate(self):
        print("Toga app: onCreate")

    def onStart(self):
        print("Toga app: onStart")

    def onResume(self):
        print("Toga app: onResume")

    def onPause(self):
        print("Toga app: onPause")

    def onStop(self):
        print("Toga app: onStop")

    def onDestroy(self):
        print("Toga app: onDestroy")

    def onRestart(self):
        print("Toga app: onRestart")

    def onActivityResult(self, requestCode, resultCode, resultData):
        """
        Callback method, called from MainActivity when an Intent ends

        :param int requestCode: The integer request code originally supplied to startActivityForResult(),
                                allowing you to identify who this result came from.
        :param int resultCode: The integer result code returned by the child activity through its setResult().
        :param Intent resultData: An Intent, which can return result data to the caller (various data can be attached
                                  to Intent "extras").
        """
        print("Toga app: onActivityResult, requestCode={0}, resultData={1}".format(requestCode, resultData))
        try:
            # remove Intent from the list of running Intents,
            # and set the result of the intent.
            result_future = self.running_intents.pop(requestCode)
            result_future.set_result({"resultCode": resultCode, "resultData": resultData})
        except KeyError:
            print("No intent matching request code {requestCode}")

    @property
    def native(self):
        # We access `MainActivity.singletonThis` freshly each time, rather than
        # storing a reference in `__init__()`, because it's not safe to use the
        # same reference over time because `rubicon-java` creates a JNI local
        # reference.
        return MainActivity.singletonThis


class App:
    def __init__(self, interface):
        self.interface = interface
        self.interface._impl = self
        self._listener = None

        self.loop = android_events.AndroidEventLoop()

    @property
    def native(self):
        return self._listener.native if self._listener else None

    def create(self):
        # The `_listener` listens for activity event callbacks. For simplicity,
        # the app's `.native` is the listener's native Java class.
        self._listener = TogaApp(self)
        # Call user code to populate the main window
        self.interface.startup()

    def open_document(self, fileURL):
        print("Can't open document %s (yet)" % fileURL)

    def main_loop(self):
        # In order to support user asyncio code, start the Python/Android cooperative event loop.
        self.loop.run_forever_cooperatively()

        # On Android, Toga UI integrates automatically into the main Android event loop by virtue
        # of the Android Activity system.
        self.create()

    def set_main_window(self, window):
        pass

    def show_about_dialog(self):
        self.interface.factory.not_implemented("App.show_about_dialog()")

    def exit(self):
        pass

    def set_on_exit(self, value):
        pass

    def add_background_task(self, handler):
        self.loop.call_soon(wrapped_handler(self, handler), self)

    async def intent_result(self, intent):
        """
        Calls an Intent and waits for its result.

        A RuntimeError will be raised when the Intent cannot be invoked.

        :param Intent intent: The Intent to call
        :returns: A Dictionary containing "resultCode" (int) and "resultData" (Intent or None)
        :rtype: dict
        """
        if intent.resolveActivity(self.native.getPackageManager()) is None:
            raise RuntimeError('No appropriate Activity found to handle this intent.')
        self._listener.last_intent_requestcode += 1
        code = self._listener.last_intent_requestcode

        result_future = asyncio.Future()
        self._listener.running_intents[code] = result_future

        self.native.startActivityForResult(intent, code)
        await result_future
        return result_future.result()
