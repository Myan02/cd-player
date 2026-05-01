from drive import Drive
from interface import initGPIO

def main():
    new_drive = Drive()
    initGPIO(new_drive)

if __name__ == "__main__": 
    main()