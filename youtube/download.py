import os, sys

from pytubefix import YouTube

print("URL:", sys.argv[1]);
YouTube( sys.argv[1] ).streams.filter(subtype='mp4', adaptive=True)[0].download(output_path=os.path.expandvars("$HOME/Downloads/"))