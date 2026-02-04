import vlc
import time
class Player:
    def __init__(self):
        self.load_audio_file()
        self.instance = vlc.libvlc_new(0, [])
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(100)
        media = self.instance.media_new('test.mp3')
        media2 = self.instance.media_new('test-2.mp3')
        self.player.set_media(media)
        self.player.set_media(media2)
        print(self.player.get_media().get_mrl())
        self.player.play()
        time.sleep(10)
        self.player.next()

    def load_audio_file(self):
        pass

Player()
while True:
    pass