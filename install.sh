#!/bin/bash

sudo apt install gh

pip3 install IPython
pip3 install kokoro
pip3 install soundfile
pip3 install argostranslate
#pip3 install googletrans
pip3 install opencv-python
pip3 install gTTS googletrans==4.0.0-rc1 pygame

pip3 install -U stable-ts
pip3 install requests
pip3 install faster-whisper

#pip3 install moviepy
# pip install moviepy==1.0.3

if [ ! -d $HOME/desenv ]
then
    mdkir $HOME/desenv
    cd $HOME/desenv
    gh repo clone naoimportaweb/nocopyright

    cd $HOME/desenv/nocopyright
    python3 ./api/argoshelp.py
fi
