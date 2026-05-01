import cdio, vlc
import os, fcntl

"""
Handle all operations related to the CD-ROM Drive
"""
class Drive():
    name = "/dev/cdrom"

    # initialize device
    def __init__(self):
        self.device = None
        self.player = None

        self.drive_type = ""
        self.status = ""

        self.track = None
        self.total_tracks = None

        self.initCDPlayer(drive_type="cdda")
    
    # set device and player api
    def initCDPlayer(self, drive_type: str = "cdda") -> None:
        try:
            # set optical device using source name
            self.device = cdio.Device(Drive.name)
            self.drive_type = drive_type

        except IOError as e:
            self.device = None
            self.player = None
            print(f"error setting up device: {e}")
            return

        try:
            # set vlc player media using dir path
            player_path = f"{drive_type}://{Drive.name}"
            self.player = vlc.MediaPlayer(player_path)

        except Exception as e:
            self.device = None
            self.player = None
            print(f"error setting up player: {e}")
            return
      
    # get current tray state
    def getTrayStatus(self) -> str:
        DRIVE_STATUS_CODE = 0x5326

        # return error if device isn't initialized; can't get tray status of an unknown drive
        if not self.device or not self.player:
            print("can't retrieve tray status, no device initialized...")
            self.status = ""
            return 

        try:
            # open the cd-rom in read only mode, return file descriptor
            fd = os.open(Drive.name, os.O_RDONLY | os.O_NONBLOCK)

            status = fcntl.ioctl(fd, DRIVE_STATUS_CODE) # sys call to get tray status
            os.close(fd)

        except Exception as e:
            print(f"drive tray error: {e}")
            self.status = ""
            return
        
        # set valid status 
        match status:
            case 0:
                self.status = "no info"

            case 1:
                self.status = "no disk"
        
            case 2:
                self.status = "tray open"
            
            case 3:
                self.status = "drive not ready"
            
            case 4:
                self.status = "disk ok"
            
            case _:
                self.status = ""
  
    # eject media and open tray
    def ejectDevice(self) -> None:
        self.getTrayStatus()

        match self.status:

            case "tray open":
                print("tray is already open")
            
            case "drive not ready":
                print("please wait...")
            
            case "no disk" | "disk ok":
                try:
                    self.player.stop()  # stop all media before ejecting

                    print("ejecting device...")
                    self.device.eject_media()   # eject media
                    print("ejection complete")

                except cdio.DriverUnsupportedError:
                    print("Eject not supported for this drive")
                except cdio.DeviceException:
                    print("something went wrong with the eject routine...")
                finally:
                    # reinitialize media player after attempted ejection
                    self.initCDPlayer(self.drive_type) 

            case _:
                print("cannot eject disk, no such device found")
        
    # play current disk
    def playMedia(self) -> None:
        self.getTrayStatus()

        match self.status:

            case "tray open":
                print("please close the tray to play media...")
            
            case "drive not ready":
                print("please wait...")
            
            case "no disk":
                print("insert a disk to play media...")

            case "disk ok":
                if self.player.is_playing():
                    self.player.pause()
                    print("media paused")
                else:
                    self.player.play()
                    self.track = self.player.audio_get_track()                  # current track
                    self.total_tracks = self.player.audio_get_track_count()     # number of tracks on disk
                    print("media playing")

            case _:
                print("cannot play media, no device found")

    # skip to next track
    def skipTrack(self) -> None:
        self.getTrayStatus()

        match self.status:

            case "tray open":
                print("please close the tray to play media...")
            
            case "drive not ready":
                print("please wait...")
            
            case "no disk":
                print("insert a disk to play media...")

            case "disk ok":
                self.track = min(self.total_tracks, self.track + 1)
                self.player.audio_set_track(self.track)
                print(f"now playing track {self.track}")

            case _:
                print("cannot play media, no device found")

    # play previous track (or replay track if paused)
    def prevTrack(self) -> None:
        self.getTrayStatus()

        match self.status:

            case "tray open":
                print("please close the tray to play media...")
            
            case "drive not ready":
                print("please wait...")
            
            case "no disk":
                print("insert a disk to play media...")

            case "disk ok":
                if not self.player.is_playing():
                    self.player.audio_set_track(self.track)
                    print(f"replaying track {self.track}")
                    return
            
                self.track = max(0, self.track - 1)
                self.player.audio_set_track(self.track)
                print(f"now playing track {self.track}")

            case _:
                print("cannot play media, no device found")

    # increase player volume
    def volumeUp(self) -> None:
        max_volume = 100
        inc_volume = self.player.audio_get_volume() + 10

        self.player.audio_set_volume(min(max_volume, inc_volume))
    
    # decrease player volume
    def volumeDown(self) -> None:
        min_volume = 0
        dec_volume = self.player.audio_get_volume() - 10

        self.player.audio_set_volume(max(min_volume, dec_volume))

    # change from dvd to cd type and vise-versa
    def changeDriveType(self, drive_type) -> None:
        
        # exit if same drive type
        if drive_type == self.drive_type:
            print(f"drive aready in {drive_type} mode, returning...")
            return

        self.getTrayStatus()

        match self.status:

            case "drive not ready":
                print("please wait...")

            case "tray open" | "no disk":
                self.initCDPlayer(drive_type)
                self.drive_type = drive_type

                print(f"drive is now in {drive_type} mode")
            
            case _:
                print("cannot change media, no device found")

    # device representation for debugging
    def __repr__(self) -> dict:
        info = {
            "device_name": self.device.get_device(),
            "device_driver_id": self.device.get_driver_id(),
            "device_driver_name": self.device.get_driver_name(),
            "HW_info": self.device.get_hwinfo(),
            "device_capabilities": self.device.get_drive_cap()
        }

        info_string = ""
        for key, val in info.items():
            info_string += f"{key}: {val}\n\n"

        return info_string
    
"""
Test function when calling this script
"""
def testDrive():
    new_drive = Drive()

    user_input = input(f"New drive initialized, press q to quit: ")
    while user_input.lower() != "q":
        
        match user_input.lower():
            case "h":
                print(new_drive)

            case "e":
                new_drive.ejectDevice()
            
            case "p": 
                new_drive.playMedia()
            
            case "u":
                new_drive.volumeUp()
            
            case "d":
                new_drive.volumeDown()
            
            case "c":
                print("what would you like to change the drive type to?")
                drive_type = input("1 = dvd  2 = cd:  ")

                if drive_type == "1":
                    new_drive.changeDriveType("dvd")

                elif drive_type == "2":
                    new_drive.changeDriveType("cdda")

                else:
                    print("invalid option")
        
        user_input = input("choose an option... ")

if __name__ == "__main__":
    testDrive()


