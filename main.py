from threading import Thread

from Display_output import Ada_pygame_prototype
from IPA_input import IPA_Calculation


class DisplayThread(Thread):
    """
    This thread class is for presenting the display on the smart-glass.
    """
    def __init__(self, name, time, PID):
        Thread.__init__(self)
        self.name = name
        self.time = time
        self.PID = PID

    def run(self):
        Ada_pygame_prototype.run_pilots(name=self.name,
                                        time=self.time,
                                        id_participant=self.PID)


class IPAThread(Thread):
    """
    This thread is for reading IPA data while running my prototype concurrently.
    """
    def __int__(self):
        Thread.__init__(self)

    def run(self) -> None:
        IPA_Calculation.run_IPA_collection()


if __name__ == '__main__':
    # Initiate the pilot study's output(display) thread.
    thread_display = DisplayThread(name='Trial',
                                   time='27 July 2022',
                                   PID=2)
    # Initialize the IPA data calculation and reading thread.
    thread_ipa = IPAThread()

    # Start the IPA thread.
    thread_ipa.start()

    # Start the display thread.
    thread_display.start()

