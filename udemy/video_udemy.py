import os, sys, traceback;
import threading, time, json;

from pathlib import Path

ROOT = os.path.expandvars("$HOME/desenv/nocopyright/");
sys.path.append(ROOT);
from api.video import Video;

engines = ["google", "gtts", "kokoro"];
raizes = [ os.path.expandvars("$HOME/cursos/") ];
CONTADOR_THREADS = 0;
TOTAL_THREADS = 1 ; #int( sys.argv[1] );

class VideoUdemy(Video):
    def __init__(self, path_video, legenda=None):
        super().__init__(path_video, legenda=legenda);

class Project():
    def __init__(self, path_directory):
        self.path_directory = path_directory;
        self.videos = [];
        self.name = None;
        self.language = None;
        self.languages = [];
        
    def find_videos(self):
        self.videos = [];
        diretorios = diretorios_recursivos( self.path_directory );
        diretorios.sort();
        for diretorio in diretorios:
            videos = VideoUdemy.load( self, diretorio );
            for video in videos:
                try:
                    if video.existe():
                        continue;
                    video.start();
                    self.videos.append(video);
                except KeyboardInterrupt:
                    exit(1)
                except:
                    traceback.print_exc();
    def start(self):
        buffer = json.loads( open( os.path.join( self.path_directory, "project.json" ) , "r" ).read() );
        self.language   = buffer["language"];
        self.name       = buffer["name"];
        self.languages  = buffer["languages"];
        self.find_videos();
        buffer = None;

def diretorios_recursivos(diretorio ):
    lista = [];
    buffers = os.listdir(diretorio);
    buffers.sort();
    for buffer in buffers:
        if buffer == "ptbr" or buffer == "eses" or buffer == "itit" or buffer == "enus":
            continue;
        path_buffer = os.path.join(diretorio, buffer);
        if os.path.isdir(path_buffer):
            lista.append(path_buffer);
            lista = lista + diretorios_recursivos(path_buffer);
    return lista;

def novo_projeto(diretorio):
    print(diretorio);
    p = Project(diretorio);
    p.start();
    try:
        for buffer in p.videos:
            buffer.legendar();
            buffer.translate();
            buffer.make_video();
            buffer.to_mp4(delete_mkv=False);
    finally:
        for buffer in p.videos:
            buffer.clear();

while True:
    threads_list = [];
    for raiz in raizes:
        diretorios = os.listdir( raiz );
        for diretorio in diretorios:
            if os.path.exists( os.path.join( raiz, diretorio, "project.json" ) ):
                project_thread = threading.Thread(target=novo_projeto, args=(os.path.join( raiz, diretorio ),))
                project_thread.start();
                threads_list.append( project_thread );
    for project_thread in threads_list:
        project_thread.join();
    break;


#def make_video(video):
#    global CONTADOR_THREADS;
#    try:
#        print("\033[96m", video.path_video, "\033[0m");
#        video.legendar();
#        video.translate("pt");
#        video.make_video("pt", sys.argv[2]);
#        video.to_mp4(delete_mkv=True);
#        video = None;
#    except KeyboardInterrupt:
#        exit(1)
#    except:
#        traceback.print_exc();
#    finally:
#        CONTADOR_THREADS = CONTADOR_THREADS - 1;

#while True:
#    try:
#        diretorios = [];
#        for raiz in raizes:
#            diretorios.append( raiz );
#            diretorios = diretorios + diretorios_recursivos(raiz);
#        diretorios.sort();
#        for diretorio in diretorios:
#            if not os.path.exists(diretorio):
#                continue;
#            videos = VideoUdemy.load( diretorio );
#            for video in videos:
#                try:
#                    if video.existe():
#                        continue;
#                    while TOTAL_THREADS <= CONTADOR_THREADS:
#                        time.sleep(10);
#                    CONTADOR_THREADS = CONTADOR_THREADS + 1;
#                    video_thread = threading.Thread(target=make_video, args=(video,))
#                    video_thread.start()       
#                except KeyboardInterrupt:
#                    exit(1)
#                except:
#                    traceback.print_exc();
#                finally:
#                    video.clear();
#    except KeyboardInterrupt:
#        exit(1)
#    except:
#        traceback.print_exc();
