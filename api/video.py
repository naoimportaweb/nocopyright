import os, sys, traceback, re, cv2, time, uuid, shutil, json;

ROOT = os.path.expandvars("$HOME/desenv/videotradutor/");
sys.path.append(ROOT);

from api.legenda import Legenda;
from datetime import datetime as dt
from faster_whisper import WhisperModel

#https://www.argosopentech.com/argospm/index/
# 1 - Palavras reservadas  <<< dicionario de palavras
# 2 - não leva em consideraçào o contexto.... << retreinar o argos tranlator

VIDEOS = [".mkv", ".mp4"];
LEGENDAS = [".vtt"];
MAX_THREADS = 2;

if not os.path.exists("/tmp/traducao/"):
    os.makedirs("/tmp/traducao/", exist_ok=True);

CONFIG_GOOGLE = None;
if os.path.exists(os.path.expandvars("$HOME/.google.json")):
    CONFIG_GOOGLE = json.loads(open(os.path.expandvars("$HOME/.google.json"), "r").read());

class Video:
    def __init__(self, project, path_video):
        self.project = project;
        self.id = str( uuid.uuid4() );
        self.path_video = path_video;
        self.filename   = self.path_video[self.path_video.rfind("/") + 1: self.path_video.rfind(".")];
        self.directory  = os.path.dirname( self.path_video );
        self.legendas = [];
        self.path_final_vtt =   os.path.join( self.directory,  self.filename + ".vtt" );
        self.tmp_path = "/tmp/file_" + self.id + ".kvm"
        cam = cv2.VideoCapture( path_video );
        self.fps = cam.get(cv2.CAP_PROP_FPS);
        self.started = True;

        self.THREADS_TRADUTOR_CONTADOR  =  0;
        self.THREADS_TRADUTOR_MAX       = 10;
        self.THREADS_TTS_CONTADOR       =  0;
        self.THREADS_TTS_MAX            = 10;
    
    def start(self):
        print("Iniciando:", "\033[97m", self.filename, "\033[0m");
        for language in self.project.languages:
            path_language = os.path.join( self.directory, language["directory"]);
            if not os.path.exists(path_language):
                os.makedirs( path_language , exist_ok=True);  

    def existe(self, language_dir = None):
        if language_dir == None:
            for language in self.project.languages:
                dir_final = os.path.join( self.directory, language["directory"] );
                file_mkv = os.path.join( dir_final, self.filename + ".mkv");
                file_mp4 = os.path.join( dir_final, self.filename + ".mp4");
                if not os.path.exists(file_mp4):
                    return False;
            return True;
        else:
            dir_final = os.path.join( self.directory, language_dir );
            file_mp4 = os.path.join( dir_final, self.filename + ".mp4");
            return os.path.exists(file_mp4);

    def legendar(self):
        if os.path.exists( self.path_final_vtt ):
            self.legendas = Legenda.load( self.path_final_vtt , self.fps );
        else:
            path_buffer = transcrever(self.path_video);
            shutil.move(path_buffer, self.path_final_vtt);
            self.legendas = Legenda.load( self.path_final_vtt, self.fps );

    def __translate__(self, legenda, to_language):
        try:
            retorno = legenda.translate( self.project.language, to_language );
        except:
            traceback.print_exc();
        finally:
            self.THREADS_TRADUTOR_CONTADOR = self.THREADS_TRADUTOR_CONTADOR - 1;

    def translate(self):
        try:
            semaforo = [];
            print(self.project.languages);
            for language in self.project.languages:
                # Verifica se já foi feito o vídeo para a cultura específica
                if self.existe(language_dir=language["directory"]):
                    continue;
                for legenda in self.legendas:
                    self.__translate__(legenda, language);
            #todo: melhorar no futuro
            #for language in self.project.languages:
            #    path_legenda = os.path.join( self.directory, language["directory"], self.filename + ".vtt" );
            #    if not os.path.exists( path_legenda ):
            #        with open(path_legenda, "w") as f:
            #            for legenda in self.legendas:
            #                f.write( legenda.traducoes[language["language"]] );
        except:
            traceback.print_exc();

    #def __make_video__(self, legenda, to_language ):
    #    try:
    #        retorno = legenda.make_video( self.path_video, to_language ); 
    #    except:
    #        traceback.print_exc();
    #    finally:
    #        self.THREADS_TTS_CONTADOR = self.THREADS_TTS_CONTADOR - 1;

    def make_video(self):
        try:
            print("Criando vídeo para: ", self.filename);
            semaforo = [];
            for language in self.project.languages:
                if self.existe(language_dir=language["directory"]):
                    continue;
                file_final = os.path.join( self.directory, language["directory"], self.filename + ".mkv" );
                if os.path.exists(file_final):
                    continue;
                file_final_mp4 = os.path.join( self.directory, language["directory"], self.filename + ".mp4" );
                if os.path.exists(file_final_mp4):
                    continue;
                with open("/tmp/"+ self.id +".txt", "w") as f:
                    for i in range(len(self.legendas)):
                        print(str(len(self.legendas) - 1), "/", i);
                        #self.__make_video__(self.legendas[i], language);
                        path_buffer = self.legendas[i].make_video( self.path_video, language ); 
                        #path_buffer = "/tmp/video_legenda_" + language["language"] + "_" + self.legendas[i].id + ".mkv";
                        if path_buffer != None and os.path.exists(path_buffer):
                            f.write("file '" + path_buffer + "'\n");
                            if i < len(self.legendas) - 1:
                                diferenca_segundos = int(self.legendas[i + 1].inicio_milisegundo/1000) - int(self.legendas[i].fim_milisegundo/1000 );
                                print("diferença: \033[91m", self.legendas[i + 1].inicio_milisegundo/1000 - self.legendas[i].fim_milisegundo/1000, "\033[0m" );
                                if diferenca_segundos > 0 and self.legendas[i + 1].do_work():
                                    path_out_silencio = "/tmp/silencio_" + str(uuid.uuid4()) + ".mkv";
                                    insert_blank_audio(self.path_video, path_out_silencio, int(self.legendas[i].fim_milisegundo/1000 ), int(self.legendas[i + 1].inicio_milisegundo/1000))
                                    f.write("file '" + path_out_silencio + "'\n");
                        else:
                            print("\033[91m", "FALHA NAO FOI ENCONTRADO UM VIDEO", self.legendas[i].texto, "\033[0m"); #  

                command = "ffmpeg -f concat -safe 0 -i '/tmp/"+ self.id +".txt' -c copy '/tmp/final_"+ language["language"] +"_"+ self.id +".mkv' > /dev/null 2>&1"; #
                os.system( command );
                dir_final = os.path.join( self.directory, language["directory"] ); 
                if not os.path.exists(dir_final):
                    os.makedirs(dir_final, exist_ok=True);
                shutil.move('/tmp/final_' + language["language"] +"_"+ self.id + '.mkv', file_final )
            self.to_mp4(delete_mkv=True);
            return True;
        except:
            traceback.print_exc();
        return False;
    
    def clear(self):
        for language in self.project.languages:
            for legenda in self.legendas:
                path_buffer = "/tmp/video_legenda_" + language["language"] + "_" + legenda.id + ".mkv";
                if os.path.exists( path_buffer ):
                    os.unlink( path_buffer );
                legenda.clear(language);
        if os.path.exists(self.tmp_path):
            os.unlink(self.tmp_path);
        if os.path.exists("/tmp/"+ self.id +".mkv"):
            os.unlink("/tmp/"+ self.id +".mkv");
        if os.path.exists( "/tmp/"+ self.id +".txt" ):
            os.unlink("/tmp/"+ self.id +".txt");

    def to_mp4(self, delete_mkv=False):
        for language in self.project.languages:
            path_mp4 = os.path.join(self.directory, language["directory"] ,self.filename) + ".mp4";
            path_mkv = os.path.join(self.directory, language["directory"] ,self.filename) + ".mkv";
            if os.path.exists( path_mkv  ):
                if os.path.exists( path_mp4 ):
                    os.unlink(path_mp4);
                #os.system("ffmpeg -i '"+ path_mkv +"' -c:v libx264 -pix_fmt yuv420p -c:a copy '"+ path_mp4 + "'  > /dev/null 2>&1")
                os.system("ffmpeg -i '"+ path_mkv +"' '"+ path_mp4 + "' > /dev/null 2>&1" ) ; #> /dev/null 2>&1
                if os.path.exists(path_mp4):
                    os.unlink(path_mkv);

    @staticmethod
    def load(project, path_dir, legenda_none=True):
        lista = os.listdir( path_dir );
        retorno = [];
        lista.sort();
        for item in lista:
            path_file = os.path.join( path_dir, item );
            path_legenda = None;
            filename, file_extension = os.path.splitext( path_file );
            if file_extension in VIDEOS:
                buffer = Video( project, path_file );
                retorno.append( buffer );
        return retorno;


def insert_blank_audio(path_video_base, path_out, second_start, second_end):
    try:
        video_base = cv2.VideoCapture( path_video_base );
        fps = video_base.get(5);
        frame_start = int(second_start  * fps);
        frame_end   = int(second_end    * fps);
        path_buffer_sem_audio   = "/tmp/" + str(uuid.uuid4()) + ".mkv";
        path_buffer_com_audio   = path_out;
        total_frames_video = frame_end - frame_start;
        video_base.set(cv2.CAP_PROP_POS_FRAMES, frame_start - 1);  #https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
        frame_width =  int(video_base.get(3));
        frame_height = int(video_base.get(4));
        frame_size =   (frame_width,frame_height);
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G');
        video_output = cv2.VideoWriter(path_buffer_sem_audio, fourcc , fps, frame_size);
        for i in range(total_frames_video):
            success, image = video_base.read();
            video_output.write( image );
        video_output.release();
        video_base.release();
        video_output = None;
        video_base = None;
        fourcc = None;

        shutil.move(path_buffer_sem_audio, path_buffer_com_audio);
        if os.path.exists(path_buffer_sem_audio):
            os.unlink( path_buffer_sem_audio );
        return path_buffer_com_audio;
    except:
        traceback.print_exc();
    return False;


def transcrever(path_video):
    start_datet_time = dt.now();
    elapsed = None;
    end = None;

    path_vtt = os.path.join("/tmp/", str(uuid.uuid4()) + ".vtt");
    model_size = "large"
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    segments, info = model.transcribe(path_video, beam_size=5)
    with open(path_vtt, "w") as f:
        for segment in segments:
            end_datet_time = dt.now();
            elapsed = end_datet_time - start_datet_time;

            sys.stdout.write( "\r\tSEGMENT: %.2fs -> %.2fs \t Processamento: %.2fs" % (segment.start, segment.end, elapsed.seconds) );
            sys.stdout.flush();
            start = segment.start; #= str(segment.start).replace(".", ":") + ".0";
            end   = segment.end; # str(segment.end  ).replace(".", ":") + ".0";
            text = segment.text.strip();
            f.write(f"{start:.2f} --> {end:.2f}\n")
            f.write(f"{text}\n\n")
    return path_vtt;
