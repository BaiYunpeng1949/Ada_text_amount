import time
from threading import Thread

from Display_output import Ada_pygame_prototype, Config
from IPA_input import IPA_Calculation


class IPAThread(Thread):
    """
    This thread is for reading IPA data while running my prototype concurrently.
    """
    def __int__(self):
        Thread.__init__(self)

    def run(self):
        IPA_Calculation.run_IPA_collection(is_3D_method=Config.IS_3D_METHOD,
                                           is_averaging_2_pupils=Config.IS_2_PUPILS)


if __name__ == '__main__':
    is_eye_gazer_started = False

    # Start the eye gazer, set everything up: TODO: hash this ipa reading thread when the "pupil labs" eye tracker is not connected to the current laptop.
    # Initialize the IPA data calculation and reading thread.
    is_eye_gazer_started = True
    thread_ipa = IPAThread()
    thread_ipa.start()

    # Start the display.
    Ada_pygame_prototype.run_pilots(name='Bai4',
                                    time='2 August 2022',
                                    id_participant=1,
                                    is_lhipa=is_eye_gazer_started
                                    )

