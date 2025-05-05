# VideoTradutor
## _De qualquer cultura para qualquer cultura_

Video Tradutor é um projeto Python que proporciona um mecanismo de tradução de vídeos, mesmo que não exista legendas o mecanismo legenda e em seguida traduz

- Legenda;
- Tradução;
- Gravação;

## Projetos que são referenciados

- Kokoro TTS (Text to Speech): https://huggingface.co/hexgrad/Kokoro-82M
- Faster Whisper (Speech to Text) : https://github.com/SYSTRAN/faster-whisper

## Instalação

Precisará de ter um Linux baseado em Debian com Python 3 instlado, precisa adicionar como super usuário:

```sh
sudo apt update -y
sudo apt install python3-pip -y
sudo apt install ffmpeg -y
```

Depois executar o script install.sh como usuário normal:

```sh
wget -O /tmp/install.sh https://raw.githubusercontent.com/naoimportaweb/videotradutor/refs/heads/main/install.sh
chmod +x /tmp/install.sh

/tmp/install.sh
```

## Licença

MIT

**Free Software, Hell Yeah!**


