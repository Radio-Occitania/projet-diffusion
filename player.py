import vlc
import time
from programation import Programation
import os
import os.path
import re
from librosa import load as LiLoad

class Player:
    def __init__(self, programation : Programation):
        self.prog = programation
        self.instance = vlc.libvlc_new(0, [])
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(100)
        self.playlist : list[list[vlc.Media], list[vlc.Media]] = [[],[]]
        self.error_record = {}
        self.__player_test__()
        self.tempo()

    def __player_test__(self):
        self.player_test = self.instance.media_player_new()
        self.player_test.audio_set_volume(0)

    def tempo(self):
        print(self.__is_audio_valid__("test.mp3"))
        """media = self.instance.media_new('test.mp3')
        media2 = self.instance.media_new('test-2.mp3')
        self.player.set_media(media)
        print(self.player.get_media().get_mrl())
        self.player.play()
        time.sleep(10)
        print(self.player.get_length())
        self.player.pause()
        time.sleep(10)
        self.player.pause()
        print(self.player.get_time())
        print(self.player.get_length()-self.player.get_time())"""

    def next(self):
        if len(self.playlist[0]) == 0: self.__load_playlist_from_programation__()

    def __load_playlist_from_programation__(self):
        self.playlist[0] = self.playlist[1][::1]
        self.playlist[1].clear()
        for i in self.prog.get_next_event():
            if os.path.isfile(i):
                if self.__is_audio__(i):
                    self.playlist[1].append(self.instance.media_new(i))

    def __is_audio_valid__(self, path_to_test):
        if self.instance.media_new_path(path_to_test):
            try:
                LiLoad(path_to_test)
                return True
            except: pass
        return False
        
prog = Programation()
Player(prog)
while True:
    pass