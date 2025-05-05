import sys, os;

ROOT = os.path.expandvars("$HOME/desenv/nocopyright/");
sys.path.append(ROOT);

from api.video import Video;

class VideoTradutor(Video):
    def __init__(self, path_video, legenda=None):
        super().__init__(path_video, legenda=legenda);