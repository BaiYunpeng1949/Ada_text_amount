import time
from threading import Thread

from Display_output import Ada_pygame_prototype
from IPA_input import IPA_Calculation


class IPAThread(Thread):
    """
    This thread is for reading IPA data while running my prototype concurrently.
    """
    def __int__(self):
        Thread.__init__(self)

    def run(self):
        IPA_Calculation.run_IPA_collection()


if __name__ == '__main__':
    # Start the eye gazer, set everything up:
    # Initialize the IPA data calculation and reading thread.
    thread_ipa = IPAThread()
    thread_ipa.start()

    time.sleep(20)  # Wait for 20s of initialization.
    print("waiting is over")

    # Start the display.
    Ada_pygame_prototype.run_pilots(name='trial',
                                    time='27 July 2022',
                                    id_participant=2
                                    )

