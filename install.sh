#!/bin/bash

# Execute no terminal como super usuario
# sudo apt update -y
# sudo apt install python3-pip -y
# sudo apt install ffmpeg -y

# Execute abaixo como usuário comum
python3 -m pip config set global.break-system-packages true

pip3 install IPython
pip3 install kokoro
pip3 install soundfile
pip3 install argostranslate
pip3 install opencv-python
pip3 install gTTS googletrans==4.0.0-rc1 pygame

pip3 install -U stable-ts
pip3 install requests
pip3 install faster-whisper

if [ ! -d $HOME/desenv ]
then
    mkdir $HOME/desenv
    wget -O /tmp/nocopiright.zip https://codeload.github.com/naoimportaweb/videotradutor/zip/refs/heads/main
    cd /tmp/
    unzip nocopiright.zip

    cd $HOME/desenv
    mkdir $HOME/desenv/videotradutor
    cp -r /tmp/videotradutor-main/* $HOME/desenv/videotradutor
    
fi
# sempre atualizar o dicionario
python3 $HOME/desenv/videotradutor/api/argoshelp.py

if [ ! -d $HOME/cursos ]
then
    mkdir $HOME/cursos
fi

if [ ! -d $HOME/tmp ]
then
    mkdir $HOME/tmp
fi
