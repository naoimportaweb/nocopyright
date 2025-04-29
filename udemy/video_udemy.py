import os, sys, traceback, time, threading, time, json, argostranslate;

from pathlib import Path
from argostranslate import package, translate

ROOT = os.path.expandvars("$HOME/desenv/nocopyright/");
sys.path.append(ROOT);

raizes = [ os.path.expandvars("$HOME/cursos/") ];
ARGOS_DIR = os.path.expandvars("$HOME/tmp/argos/");

from api.video import Video;

CONTADOR_THREADS = 0;
TOTAL_THREADS = 1;

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
        self.installed_languages = None;
        self.active = True;
        self.max_threads = 2;
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
        if buffer.get("max_threads") != None:
            self.max_threads     = buffer["max_threads"];
        else:
            self.max_threads     = 2;
        if buffer.get("effects") != None:
            self.active     = buffer["active"];
        else:
            self.active     = False;
        if buffer.get("effects") != None:
            self.effects    = buffer["effects"];
        else:
            self.effects    = [];
        if self.active == True:
            for language_buffer in self.languages:
                if self.language != language_buffer["language"]:
                    if self.language == "en" or language_buffer["language"] == "en":
                        path_model = os.path.join( ARGOS_DIR, "translate-"+ self.language +"_"+ language_buffer["language"] +".argosmodel"  );
                        if os.path.exists(path_model):
                            package.install_from_path( path_model );
                            print("\033[92m", "Model carregado:",path_model , "\033[0m");
                    else:
                        path_model = os.path.join( ARGOS_DIR, "translate-en_"+ language_buffer["language"] +".argosmodel"  );
                        if os.path.exists(path_model):
                            package.install_from_path( path_model );
                            print("\033[92m", "Model carregado:",path_model , "\033[0m");
                        path_model = os.path.join( ARGOS_DIR, "translate-"+ self.language +"_en.argosmodel"  );
                        if os.path.exists(path_model):
                            package.install_from_path( path_model );
                            print("\033[92m", "Model carregado:",path_model , "\033[0m");
            self.installed_languages = translate.get_installed_languages();
            print( "Tradução disponível para: ", [str(lang) for lang in self.installed_languages] );
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

def novo_projeto(diretorio, transcribe, translate, make):
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
    try:
        threads_list = [];
        for raiz in raizes:
            diretorios = os.listdir( raiz );
            for diretorio in diretorios:
                if os.path.exists( os.path.join( raiz, diretorio, "project.json" ) ):
                    project_thread = threading.Thread(target=novo_projeto, args=(os.path.join( raiz, diretorio ), True, True, True,))
                    project_thread.start();
                    threads_list.append( project_thread );
        for project_thread in threads_list:
            project_thread.join();
    except:
        print("mais uma volta");
    finally:
        print("pausa");
        time.sleep(120);

