from drive import Drive
from gpiozero import Button
from signal import pause


def initGPIO(drive: Drive) -> None:

    buttons: dict[Button] = {
        "volumeUp": Button(5),
        "volumeDown": Button(6),
        "play": Button(23),
        "next": Button(24),
        "prev": Button(25)
    }

    buttons["volumeUp"].when_pressed = drive.volumeUp
    buttons["volumeDown"].when_pressed = drive.volumeDown
    buttons["play"].when_pressed = drive.playMedia
    buttons["next"].when_pressed = drive.skipTrack
    buttons["prev"].when_pressed = drive.prevTrack

    pause()


