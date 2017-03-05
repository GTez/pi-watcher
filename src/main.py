from __future__ import unicode_literals
from livestreamer import Livestreamer
from omxplayer import OMXPlayer
from flask import Flask, render_template
from youtube_dl import YoutubeDL

app = Flask(__name__)
PLAYING_STREAM = None
TWITCH_OAUTH_TOKEN = '9dlozvvvlswtrtp1gkemqhz13fn7nq'

def get_streamer(name):
    streamer = Livestreamer()
    streamer.set_plugin_option('twitch', 'oauth_token', TWITCH_OAUTH_TOKEN)
    return streamer.streams('https://www.twitch.tv/{0}'.format(name))


class Stream:
    def __init__(self, stream_url, referal):
        self.stream_url = stream_url
        self.player = OMXPlayer(self.stream_url)
        self.player.pause()
        self.referal = referal

    def __del__(self):
        global PLAYING_STREAM
        self.player.quit()
        PLAYING_STREAM = None


@app.route('/')
def index():
    return render_template('index.html',
                           message="Try <a href='/twitch/start/annemuntion'>/twitch/start/annemuntion</a> !")


@app.route('/twitch/play/<name>')
def start_twitch(name):
    global PLAYING_STREAM
    if PLAYING_STREAM is None:
        PLAYING_STREAM = Stream(get_streamer(name)['best'].url, 'Twitch')
        PLAYING_STREAM.player.play()
        return render_template('index.html', message="Starting {0}".format(name))
    elif PLAYING_STREAM.player._is_playing is False:
        PLAYING_STREAM.__del__()
        PLAYING_STREAM = None
    elif PLAYING_STREAM.player._is_playing is True:
        return render_template('index.html', message='video already playing')


@app.route('/stop')
def twitch():
    global PLAYING_STREAM
    if PLAYING_STREAM is not None:
        PLAYING_STREAM.__del__()
    PLAYING_STREAM = None
    return render_template('index.html', message='stopped...')


@app.route('/pause')
def pause():
    global PLAYING_STREAM
    if PLAYING_STREAM is not None:
        PLAYING_STREAM.player.pause()
    return render_template('index.html', message='Paused')


@app.route('/unpause')
def unpause():
    global PLAYING_STREAM
    if PLAYING_STREAM is not None and PLAYING_STREAM.player._is_playing is False:
        PLAYING_STREAM.player.play()
    return render_template('index.html', message='UnPaused')


@app.route('/status')
def status():
    global PLAYING_STREAM
    if PLAYING_STREAM is None:
        status = 'Stopped'
    elif PLAYING_STREAM.player._is_playing is True:
        status = 'Playing {0} Video'.format(PLAYING_STREAM.referal)
    elif PLAYING_STREAM.player._is_playing is False:
        status = 'Paused {0} Video'.format(PLAYING_STREAM.referal)
    return render_template('index.html', message=status)


@app.route('/youtube/play/<url>')
def play_youtube(url):
    global PLAYING_STREAM
    if PLAYING_STREAM is None:
        ydl = YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
        with ydl:
            result = ydl.extract_info('https://www.youtube.com/watch?v={0}'.format(url), download=False)
        if 'entries' in result:
            # Can be a playlist or a list of videos
            video = result['entries'][0]
        else:
            # Just a video
            video = result

        PLAYING_STREAM = Stream(video['url'], 'Youtube')
        PLAYING_STREAM.player.play()
        return render_template('index.html', message='Playing {0}'.format(video['title']))
    elif PLAYING_STREAM.player._is_playing is False:
        PLAYING_STREAM.__del__()
        PLAYING_STREAM = None
        return render_template('index.html', message='Something Went Wrong, Try again')
    elif PLAYING_STREAM.player._is_playing is True:
        return render_template('index.html', message='video already playing')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)  # TODO: Set to False

