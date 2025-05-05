import os, sys, traceback, time, threading, time, json, argostranslate;

#from pathlib import Path
#from argostranslate import package, translate

ROOT = os.path.expandvars("$HOME/desenv/videotradutor/");
sys.path.append(ROOT);

raizes = [ os.path.expandvars("$HOME/cursos/") ];

from api.projeto import Projeto;

#def diretorios_recursivos(diretorio ):
#    lista = [];
#    buffers = os.listdir(diretorio);
#    buffers.sort();
#    for buffer in buffers:
#        if buffer == "ptbr" or buffer == "eses" or buffer == "itit" or buffer == "enus":
#            continue;
#        path_buffer = os.path.join(diretorio, buffer);
#        if os.path.isdir(path_buffer):
#            lista.append(path_buffer);
#            lista = lista + diretorios_recursivos(path_buffer);
#    return lista;

def novo_projeto(diretorio, transcribe, translate, make):
    while True:
        try:
            p = Projeto(diretorio);
            p.start();
            try:
                for buffer in p.videos:
                    print( buffer.filename );
                    buffer.legendar();
                    buffer.translate();
                    buffer.make_video();
                    buffer.to_mp4(delete_mkv=True);
            finally:
                for buffer in p.videos:
                    buffer.clear();
        except KeyboardInterrupt:
            break;
        except:
            traceback.print_exc();
        #finally:
        #    time.sleep(300);
        break;

def main():
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
        except KeyboardInterrupt:
            break;
        except:
            print("mais uma volta");
        #finally:
        #    print("pausa");
        #    time.sleep(120);
        print("fim..");
        break;


if __name__ == "__main__":
    main();

