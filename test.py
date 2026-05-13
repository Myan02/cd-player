import vlc
import time

instance = vlc.Instance()
player = instance.media_player_new()
medialist = instance.media_list_new()
list_player = instance.media_list_player_new()

list_player.set_media_player(player)

media = instance.media_new("cdda:///dev/cdrom")
medialist.add_media(media)
list_player.set_media_list(medialist)

list_player.play()

while True:
    time.sleep(1)
