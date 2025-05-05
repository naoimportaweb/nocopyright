import os, sys

from pytubefix import YouTube

print("URL:", sys.argv[1]);
YouTube( sys.argv[1] ).streams.filter( progressive=True )[0].download(output_path=os.path.expandvars("$HOME/Downloads/"))

