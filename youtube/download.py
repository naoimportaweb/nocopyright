import os, sys, traceback;

from pytubefix import YouTube
from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()


def transcrever(video_id):
    try:
        transcript_list = ytt_api.list(video_id);
        for transcript in transcript_list:
            if transcript.is_generated == False:
                continue;
            language = transcript.language_code.lower();
            #if not exist_language(language):
            #    raise("Não existe a language: " + language);
            original = [];
            for snippet in transcript.fetch():
                buffer_texto = snippet.text;
                buffer_texto = buffer_texto.replace("[Músic]", "");
                if buffer_texto == "" or buffer_texto == None:
                    continue;
                original.append(       { "start" : int(snippet.start) , "end" : int(snippet.start + snippet.duration), "text" : buffer_texto.strip() });
            return original;
            #return  {"version" : "1", "mode" : "youtube", "language" : language, "original" : original};
    except:
        traceback.print_exc();
        print("Não deu para transcrever a url: ", video_id);
    return None;


url = sys.argv[1];
print("URL:", url);
stream = YouTube( sys.argv[1] ).streams.filter( progressive=True )[0];
buffer_lines = transcrever( url[url.rfind("=") + 1:] );

with open(os.path.expandvars("$HOME/Downloads/") + stream.default_filename + ".vtt", "w") as f:
    for i in range(len(buffer_lines)):
        buffer = buffer_lines[i];
        if i < len(buffer_lines) - 1:
            buffer["end"] = buffer_lines[i + 1]["start"];
        f.write( str( buffer["start"] ) + ".0 --> " + str( buffer["end"] ) + ".0\n" );
        f.write( buffer["text"] + "\n\n");

stream.download(output_path=os.path.expandvars("$HOME/Downloads/"))


