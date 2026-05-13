import cdio, pycdio, vlc
import os, fcntl

"""
Handle all operations related to the CD-ROM Drive
"""
class Drive():

    # initialize device
    def __init__(self):
        self.device = None
        self.device_path = ""
        self.device_type = ""

        self.media_list = None
        self.list_player = None

        self.status = ""

        self.track = None
        self.total_tracks = None

        self.initCDPlayer(device_type="cdda")
    
    # set device and player api
    def initCDPlayer(self, device_type: str = "cdda") -> None:
        try:
            # set optical device based on unknown driver name
            self.device = cdio.Device(driver_id=pycdio.DRIVER_UNKNOWN)

            self.device_path = self.device.get_device()
            self.device_type = device_type

        except IOError as e:
            self.device = None
            self.device_type = ""
            self.device_path = ""

            self.media_list = None
            self.list_player = None

            print(f"error setting up device: {e}")
            return

        try:
            instance = vlc.Instance()

            # initialize media list (list of all tracks from cd)
            media = instance.media_new(f"{self.device_type}://{self.device_path}")
            self.media_list = instance.media_list_new([media])

            # configure list player (player that manages the track list)
            self.list_player = instance.media_list_player_new()
            self.list_player.set_media_list(self.media_list)      

        except Exception as e:
            self.device = None
            self.device_type = ""
            self.device_path = ""

            self.media_list = None
            self.list_player = None

            print(f"error setting up list player: {e}")
            return
      
    # get current tray state
    def getTrayStatus(self) -> str:
        DRIVE_STATUS_CODE = 0x5326

        # return error if device isn't initialized; can't get tray status of an unknown drive
        if not self.device or not self.list_player:
            print("can't retrieve tray status, no device initialized...")
            self.status = ""
            return 

        try:
            # open the cd-rom in read only mode, return file descriptor
            fd = os.open(self.device_path, os.O_RDONLY | os.O_NONBLOCK)

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
                    self.list_player.stop()  # stop all media before ejecting

                    print("ejecting device...")
                    self.device.eject_media()   # eject media
                    print("ejection complete")

                except cdio.DriverUnsupportedError:
                    print("Eject not supported for this drive")
                except cdio.DeviceException:
                    print("something went wrong with the eject routine...")
                finally:
                    # reinitialize media player after attempted ejection
                    self.initCDPlayer(self.device_type) 

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
                if self.list_player.is_playing():
                    self.list_player.pause()
                    print("media paused")

                else:
                    self.list_player.play()
                    print(f"media playing")

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
                self.list_player.next()
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
                if not self.list_player.is_playing():
                    # self.player.audio_set_track(self.track)
                    print(f"replaying track {self.track}")
                    return
            
                # self.track = max(0, self.track - 1)
                # self.player.audio_set_track(self.track)
                self.list_player.previous()
                print(f"now playing track {self.track}")

            case _:
                print("cannot play media, no device found")

    # increase player volume
    def volumeUp(self) -> None:
        max_volume = 100
        inc_volume = self.list_player.get_media_player().audio_get_volume() + 10

        self.list_player.get_media_player().audio_set_volume(min(max_volume, inc_volume))
    
    # decrease player volume
    def volumeDown(self) -> None:
        min_volume = 0
        dec_volume = self.list_player.get_media_player().audio_get_volume() - 10

        self.list_player.get_media_player().audio_set_volume(max(min_volume, dec_volume))

    # change from dvd to cd type and vise-versa
    def changeDriveType(self, device_type) -> None:
        
        # exit if same drive type
        if device_type == self.device_type:
            print(f"drive aready in {device_type} mode, returning...")
            return

        self.getTrayStatus()

        match self.status:

            case "drive not ready":
                print("please wait...")

            case "tray open" | "no disk":
                self.initCDPlayer(device_type)
                self.device_type = device_type

                print(f"drive is now in {device_type} mode")
            
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
            
            case "n":
                new_drive.skipTrack()
            
            case "b":
                new_drive.prevTrack()
            
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


