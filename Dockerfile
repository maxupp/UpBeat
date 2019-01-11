FROM continuumio/miniconda3

RUN pip install ffmpeg-python \
                   youtube-dl \
                   cherrypy \
                   pafy

RUN mkdir /upbeat
RUN mkdir /upbeat/snippets

RUN chmod 777 /tmp
RUN apt update
RUN apt install -y ffmpeg

COPY main.py /upbeat/main.py

ENTRYPOINT ["python", "/upbeat/main.py", "-w", "/upbeat/snippets"]
