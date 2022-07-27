from Display_output import Ada_pygame_prototype
from IPA_input import IPA_Calculation

if __name__ == '__main__':
    # Do the pilot studies. Do not run this with prototype.
    print("It started!")
    Ada_pygame_prototype.run_pilots(name="Trial",
                                    time="27 July 2022",
                                    id_participant=1)
