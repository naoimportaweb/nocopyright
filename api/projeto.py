import sys, os;
import os, sys, traceback, json, argostranslate;

ROOT = os.path.expandvars("$HOME/desenv/nocopyright/");
sys.path.append(ROOT);

from pathlib import Path
from argostranslate import package, translate

ARGOS_DIR = os.path.expandvars("$HOME/tmp/argos/");

from api.video_tradutor import VideoTradutor;

class Projeto():
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
        diretorios = os.listdir( self.path_directory );
        diretorios.sort();
        for diretorio in diretorios:
            diretorio = os.path.join( self.path_directory, diretorio );
            if not os.path.isdir( diretorio ): #todo: isso é feio....
                continue;
            videos = VideoTradutor.load( self, diretorio );
            for video in videos:
                try:
                    if video.existe(): # já foi traduzido, não precisa mais ser feito nada
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
        self.active     = buffer["active"];
        if self.active == True:
            
            for buffer_language in buffer["languages"]:   #todo: transofrmar isso em classe porraaaa
                if buffer_language["active"] == True:
                    self.languages.append( buffer_language );
            
            for language_buffer in self.languages:
                if self.language != language_buffer["language"]:
                    # tem que instalar todos os modelos requeridos, ou seja, todas as linugas
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
            self.find_videos();
            buffer = None;


# DIRETORIO DO CURSO
#       DIRETORIO DO MODULO
#           VIDEO
#           VIDEO
#           VIDEO
#       DIRETORIO DO MODULO
#           VIDEO
#           VIDEO
#           VIDEO