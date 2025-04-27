import os, sys

from pytubefix import YouTube

print("URL:", sys.argv[1]);
YouTube( sys.argv[1] ).streams.filter( progressive=True )[0].download(output_path=os.path.expandvars("$HOME/Downloads/"))

#subtype='mp4',adaptive=True
#QString command = "ffmpeg -i '"+ path_file_output_sem_audio +"' -i '"+ audiomp3 +"' -c:v copy -c:a aac '"+ path_file_output_COM_audio +"' > /dev/null 2>&1";
#QString command = "ffmpeg -i "+ mp3 +" -af 'rubberband=tempo=1.0:pitch=0."+ QString::number( Project::instance()->getPitch() ) +":pitchq=quality' " + mp3_ + " 2>/dev/null";
#
#