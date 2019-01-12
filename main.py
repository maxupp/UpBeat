# -*- coding: utf-8 -*-
import cherrypy
import os
import argparse
import youtube_dl
import re
from subprocess import call
import pathlib


def parse_args():
    parser = argparse.ArgumentParser(
        description=('UpBeat Quiz Server'))
    parser.add_argument('-w', '--work_dir', help='Path to MP3 work dir.')
    return parser.parse_args()


class SpeedpilotServer(object):

    def __init__(self, work_dir):
        self.counter = 0
        self.workdir = pathlib.Path(work_dir)
        self.db = {}

    def cut_audio(self, file, start=0):
        snippets = []

        for l in [1, 2, 3, 5, 10]:
            out_path = self.workdir / f"{str(file).rsplit('.', maxsplit=1)[0]}_{l}.mp3"
            snippets.append(out_path.name)
            cmd = f'ffmpeg -y -i {self.workdir / file} -vn -ss {start} -t {l} {out_path}'
            call(cmd, shell=True)

        return snippets

    @cherrypy.expose
    def index(self):

        html = """
        <!DOCTYPE html>
        <html lang="de">
        <head>
            <meta charset="utf-8">
            <title>UpBeat</title>
            <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
            <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/css/bootstrap.min.css">
            <link rel="stylesheet" href="assets/style.css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.5/js/bootstrap.min.js"></script>
        </head>
        <body>
        <div class="bg">
            <div class="container">
                <div class="centered">
                    <h1 class="display-1">UpBeat Music Quiz</h1>
                    <form method="get" action="build_snippet" class="form-inline form-large">
                        <input type="text" class="form-control form-control-lg" name="youtube_url" placeholder="youtube url...">
                        <input type="submit" value="Go!" class="btn btn-primary mb-2">
                    </form>
                </div>
        
            </div>
        </div>
        """
        return html

    @cherrypy.expose
    def build_snippet(self, youtube_url):
        print('PENISSSSS')
        self.counter += 1
        path = self.workdir / f'{self.counter}.tmp'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(path)
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            x = ydl.download([youtube_url])
            print(x)

        # if timestamp: start there
        print(youtube_url)
        timestamp_match = re.search("t=(\d+)$", youtube_url)

        if timestamp_match:
            snippets = self.cut_audio(path, timestamp_match.group(1))
        else:
            snippets = self.cut_audio(path)

        # delete original
        os.remove(path)

        # build page
        html = ''

        for i, snippet in enumerate(snippets):
            html += f"""
                <audio id="snippet_{i}" 
                  controls
                  src="snippets/{snippet}" 
                  type="audio/mp3" 
                ></audio> <br>
            """
        self.db[str(self.counter)] = {
            'url': youtube_url,
            'html': html
        }
        raise cherrypy.HTTPRedirect(f"quiz_page?snippet_id={self.counter}")

    @cherrypy.expose
    def quiz_page(self, snippet_id):
        if snippet_id not in self.db.keys():
            return 'Quiz ID nicht gefunden.'
        else:
            return self.db[snippet_id]['html']


if __name__ == '__main__':
    args = parse_args()
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy_config = {
        '/snippets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': args.work_dir
        },
        '/assets': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.abspath(os.path.dirname(__file__)) + '/assets'
        }
    }
    cherrypy.quickstart(SpeedpilotServer(args.work_dir), '/', cherrypy_config)

