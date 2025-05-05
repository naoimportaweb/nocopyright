import os, sys, traceback, re, cv2, uuid, shutil, hashlib, json, base64, requests;
import subprocess, argostranslate, torch;
import soundfile as sf

#           VOICES              
#https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md#italian
#           TRANSLATE ARGOS MODELS
#https://github.com/argosopentech/argospm-index?tab=readme-ov-file
from argostranslate import package, translate

from datetime import datetime as dt
from kokoro import KPipeline
from IPython.display import display, Audio
#from googletrans import Translator
#https://gtts.readthedocs.io/en/latest/module.html#localized-accents
from gtts import gTTS  # LIXO QUE VOU RREMOVER, ESSA BOSTA NÁO É OFF
from moviepy.editor import *    # É UMA BOSTA CHEIA DE MEMORY LEAK
from faster_whisper import WhisperModel


class Legenda:
    def __init__(self, texto, inicio, fim, fps, index=0):
        self.id = str( uuid.uuid4()  ) + str(index);
        self.texto  = texto.strip();
        self.inicio = inicio;
        self.fps    = fps;
        self.fim    = fim;
        #self.video  = video;
        self.inicio_milisegundo = None;
        self.fim_milisegundo    = None;
        self.traducoes = {};
        partes = re.findall("[0-9]+", self.inicio);
        if len(partes) == 3:
            self.inicio_milisegundo = (int(partes[0]) * 60 * 1000) + (int(partes[1]) * 1000) + int(partes[2]);
        else:
            self.inicio_milisegundo = (int(partes[0]) * 1000) + int(partes[1]);
        partes = re.findall("[0-9]+", self.fim);
        if len(partes) == 3:
            self.fim_milisegundo = (int(partes[0]) * 60 * 1000) + (int(partes[1]) * 1000) + int(partes[2]);
        else:
            self.fim_milisegundo = (int(partes[0]) * 1000) + int(partes[1]);
        if self.texto[-1] == ".":
            self.texto = self.texto[:-1].strip();
    
    def make_video(self, path_video, to_language):
        if not self.do_work():
            return None;
        for rodada in range(5):
            translated_text = self.traducoes[to_language["language"]];
            path_mp3 = self.make_audio(translated_text, to_language, to_language["engine"]);
            if path_mp3 != None:
                path_out = "/tmp/video_legenda_" + to_language["language"] + "_" + self.id + ".mkv";
                if os.path.exists(path_out):
                    return path_out; # já existe pois pode estar tentando novamente....
                insert_audio_in_video(path_video, path_mp3, path_out, int(self.inicio_milisegundo/1000), int( self.fim_milisegundo/1000 ) )
                if os.path.exists(path_out):
                    os.unlink(path_mp3);
                    return path_out;
            else:
                print("\033[91m", "FALHA NAO FOI ENCONTRADO UM AUDIO", "\033[0m");
        return None;

    def make_audio(self, translated_text, to_language, engine_tts):
        for tentativas in range(5):
            path_mp3 = "/tmp/" + to_language["language"] + "_" + self.id + ".mp3";
            if os.path.exists(path_mp3):
                return path_mp3;
            if engine_tts == "google":
                gravar_google( translated_text, to_language["voice"], to_language["languageCode"], path_mp3);
            elif engine_tts == "gtts":
                gravar_gtts(   translated_text, path_mp3);
            elif engine_tts == "kokoro":
                gravar_kokoro( translated_text, to_language, path_mp3);
            else:
                return None;
            if os.path.exists( path_mp3 ):
                return path_mp3;
        return None;

    def translate(self, from_language, to_language):
        try:
            from_code = from_language;
            to_code = to_language["language"];
            print("\033[96m", from_code, "->", to_code, "\033[0m", self.texto);
            if to_code == from_code or not self.do_work():
                self.traducoes[to_language["language"]] = self.texto;
            else:
                if to_code == "en" or from_code == "en":
                    self.traducoes[to_language["language"]] = argostranslate.translate.translate(self.texto, from_code, to_code);
                else:
                    buffer_traduzido = self.traducoes[to_language["language"]] = argostranslate.translate.translate(self.texto, from_code, "en");
                    self.traducoes[to_language["language"]] = argostranslate.translate.translate( buffer_traduzido , "en", to_code);
            return self.traducoes[to_language["language"]];
        except:
            traceback.print_exc();
            return None;

    def frame_start(self):
        return int((self.fps / 1000) * self.inicio_milisegundo );
    
    def frame_end(self):
        return int((self.fps / 1000) * self.fim_milisegundo );
    
    def to_string(self):
        return str(self.frame_start()) + " -> " + str(self.frame_end()) + ": " + self.texto;
    def  do_work(self):
        if self.texto == "<DELETE>":
            return False;
        return True;
    def clear(self, language):
        if os.path.exists("/tmp/" + self.id + ".mp3"):
            os.unlink("/tmp/" + self.id + ".mp3");
        if os.path.exists("/tmp/" + self.id + ".mp4"):
            os.unlink("/tmp/" + self.id + ".mp4");
        if os.path.exists("/tmp/" + self.id + ".mkv"):
            os.unlink("/tmp/" + self.id + ".mkv");
        if os.path.exists("/tmp/" + language["language"] + "_" + self.id + ".mkv"):
            os.unlink("/tmp/" + language["language"] + "_" + self.id + ".mkv");

    @staticmethod
    def load(path_file, fps):
        #teste = 0;
        filename, file_extension = os.path.splitext( path_file );
        legendas = [];
        linhas = open(path_file, "r").readlines();
        if file_extension == ".vtt":
            #00:01.910 --> 00:02.150
            #Right
            try:
                for i in range(len(linhas) - 1, 0, -1):
                    linha = linhas[i].strip();
                    if linha == "":
                        linhas.pop(i);
                        continue;
                i = 0;
                while i < len(linhas):
                    if linhas[i].find(":") > 0:
                        segundos = re.findall("[0-9]+:[0-9]+.[0-9]+", linhas[i]);
                        if len(segundos) == 2:
                            legenda = Legenda(linhas[i + 1], segundos[0], segundos[1], fps, index=i);
                            legendas.append( legenda );
                            i = i + 1;
                    else:
                        segundos = re.findall("[0-9]+.[0-9]+", linhas[i]);
                        if len(segundos) > 0:
                            legenda = Legenda(linhas[i + 1], segundos[0], segundos[1], fps, index=i);
                            legendas.append( legenda );
                            i = i + 1;
                    i = i + 1;
            except:
                if os.path.exists(path_file):
                    os.unlink(path_file);
                return None;
        return legendas;

# ----------------- grande gambibarra --------------------- CANSADO PRA CARALEO

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

def gravar_google(text, voice, languageCode, path_mp3):
    if text[-1] == ".":
        text = text[:-1];
    text = text.replace(". ", " ");
    url = "https://texttospeech.googleapis.com/v1beta1/text:synthesize"
    data = {
            "input": {"text": text},
            "voice": {"name":  voice, "languageCode": languageCode},
            "audioConfig": {"audioEncoding": "MP3"}
          };
    headers = {"content-type": "application/json", "X-Goog-Api-Key": CONFIG_GOOGLE["key"] }
    r = requests.post(url=url, json=data, headers=headers)
    content = json.loads(r.content)
    with open(path_mp3, "wb") as f:
        f.write( base64.b64decode( content["audioContent"] ) );
    return path_mp3

def gravar_gtts(text, path_mp3):
    speak = gTTS(text=translated_text, lang=to_language, slow=False);
    speak.save(path_mp3);
    return path_mp3;

def gravar_kokoro(text, language, path_mp3):
    pipeline = KPipeline(lang_code=language["language_code"], repo_id='hexgrad/Kokoro-82M');
    generator = pipeline(text, speed=0.85, voice=language["voice"]);
    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(path_mp3, audio, 24000);
    pipeline = None;
    generator = None;
    return path_mp3;

def mp3_total_frames(filename, fps):
    # se tem 1.9 segundo e 30 frames por segundo, dá para achar quantos frames precisa
    args=("ffprobe", "-show_entries", "format=duration","-i",filename)
    popen = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = popen.communicate()
    output = output.decode();   
    segundos = re.findall(r'[0-9]+.[0-9]', str(output))[0]; #todo arquivo nao existe e nao achou o INDEX
    total = int(segundos.split(".")[0]) * fps ;
    if int(segundos.split(".")[1]) > 0:
        total = total + (( int(segundos.split(".")[1]) / 10 ) * fps);
    popen = None;
    output = None;
    err = None;
    return int(total);


def insert_audio_in_video(path_video_base, path_audio, path_out, second_start, second_end):
    try:
        video_base = cv2.VideoCapture( path_video_base );
        fps = video_base.get(5);
        frame_start = int(second_start  * fps);
        frame_end   = int(second_end    * fps);
        video_base.set(cv2.CAP_PROP_POS_FRAMES, frame_start - 1);  #https://stackoverflow.com/questions/33650974/opencv-python-read-specific-frame-using-videocapture
        path_buffer_sem_audio = "/tmp/" + str(uuid.uuid4()) + ".mkv";
        path_buffer_com_audio = path_out;
        total_frames_audio = mp3_total_frames( path_audio, fps ); #TODO arquivo nao existe...
        total_frames_video = frame_end - frame_start;
        diferenca_quadros = abs( total_frames_video - total_frames_audio  );
        quadro_mod = 0;
        if diferenca_quadros > 0:
            quadro_mod = int(total_frames_video/diferenca_quadros);
        if quadro_mod == 0:
            quadro_mod = total_frames_video;
        
        frame_width = int(video_base.get(3));
        frame_height = int(video_base.get(4));
        frame_size = (frame_width,frame_height);
        fourcc = cv2.VideoWriter_fourcc('M','J','P','G');
        video_output = cv2.VideoWriter(path_buffer_sem_audio, fourcc , fps, frame_size);
        adicionados = 0;
        if second_end - second_start != 0:
            for i in range(total_frames_video):
                success, image = video_base.read()
                if diferenca_quadros == 0:
                    video_output.write( image );
                    adicionados = adicionados + 1;
                else:
                    if total_frames_video < total_frames_audio:
                        video_output.write( image );
                        adicionados = adicionados + 1;
                        if i % quadro_mod == 0:
                            video_output.write( image );
                            adicionados = adicionados + 1;
                    else:
                        if i % quadro_mod != 0:
                            video_output.write( image );
                            adicionados = adicionados + 1;
        else:
            success, image = video_base.read()
            for i in range(total_frames_audio):
                video_output.write( image );
                adicionados = adicionados + 1;
                print(".", end="");
        if adicionados < total_frames_audio: # se for menor, muito menor, dá pau, entao melhor repetir ultimo quadro....
            success, image = video_base.read();
            for i in range(total_frames_audio - adicionados):
                video_output.write( image );
                print(".", end="");
        video_output.release();
        video_base.release();
        video_output = None;
        video_base = None;
        fourcc = None;
        command = "ffmpeg -i '"+ path_buffer_sem_audio +"' -i '"+ path_audio +"' -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 '"+ path_buffer_com_audio +"' > /dev/null 2>&1 " 
        os.system(command);
        if os.path.exists(path_buffer_sem_audio):
            os.unlink( path_buffer_sem_audio );
        if not os.path.exists(path_buffer_com_audio): # deu algum tipo de pau no gerador, isso é até normal
            print("\033[96m", path_out, "start:", second_start, "end:", second_end, "vid:", total_frames_video, "aud:" ,total_frames_audio,  "\033[0m");
            return None;
        return path_buffer_com_audio;
    except:
        traceback.print_exc();
    return False;