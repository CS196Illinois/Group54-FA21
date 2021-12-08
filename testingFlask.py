from flask import Flask, request, render_template

# spotify python api imports
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# imports for graphing and spotify api
import matplotlib.pyplot as plt
plt.switch_backend('Agg')
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import numpy as np
import spotipy as sp
import pandas as pd
import io 
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask(__name__)

@app.route("/")
def hello_world():
    return ''' <label for="url">Playlist URL:</label>
    <input type="text" id="url"><br><br>
    <button onClick=window.location.replace('http://127.0.0.1:5000/bruh?url='+document.getElementById('url').value)>Click Me!</button> '''

@app.route("/bruh")
def bruh():
    r = request.values.get('url')
    # accessing spotify application through credentials
    cid = '5b85a9af539f47da8dcbbcf517e42650'
    secret = 'cb3ce73abd464866b285015d631ca1d5'
    clientCredentialsManager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
    sp = spotipy.Spotify(client_credentials_manager = clientCredentialsManager)

    valenceForEmotion = {} # for lasya

    # method to access playlist and obtain song data
    def accessPlaylist(url, limit, offset):
        # create an empty list and an empty df
        listOfFeatures = ['artist', 'album', 'trackName', 'trackId', 'danceability', 'energy', 'loudness',
                                'valence', 'tempo', 'acousticness']
        playlistDf = pd.DataFrame(columns = listOfFeatures)
        playlist = sp.user_playlist_tracks('', url, limit=limit, offset=offset)["items"]

        # loop through the given playlist and get song features
        for track in playlist:
            # create empty dict
            playlistFeatures = {}
            # get song data
            playlistFeatures['artist'] = track['track']['album']['artists'][0]['name']
            playlistFeatures['album'] = track['track']['album']['name']
            playlistFeatures["trackName"] = track["track"]["name"]
            playlistFeatures["trackId"] = track["track"]["id"]
            playlistFeatures["popularity"] = track["track"]["popularity"]
            playlistFeatures["albumReleaseDate"] = track["track"]["album"]["release_date"]
            audioFeatures = sp.audio_features(playlistFeatures["trackId"])[0]
            
            # get song features
            for feature in listOfFeatures[4:]:
                playlistFeatures[feature] = audioFeatures[feature]
                # DO NOT DELETE - LASYA NEEDS FOR VALENCE ANALYSIS 
                if (feature == "valence"):
                    valenceForEmotion[playlistFeatures['trackName']] = audioFeatures["valence"]
            
            trackDf = pd.DataFrame(playlistFeatures, index = [0])
            playlistDf = pd.concat([playlistDf, trackDf], ignore_index = True)
        # TEST --> print(playlistDf.valence[2])
        return playlistDf

    try:
        songs = accessPlaylist(r, 100, 0)
    except:
        songs = accessPlaylist('https://open.spotify.com/playlist/2U9q9cml8EInaiYFDYwZ73?si=1f188bb952c041c1', 100, 0)

    totalValence = 0.0
    count = 0
    songsForEmotion = []
    graphHeight = []
    colorsForEmotion = []

    # looping through valence values
    for key, value in valenceForEmotion.items():
        totalValence += value
        count += 1
        songsForEmotion.append(count) 
        graphHeight.append(1) # every bar will have same height
        # print("The valence of " + key + " is " + str(value))
        
        # adjusting the color of the bar based on the song's happiness
        if (value < 0.3):
            colorsForEmotion.append("black")
        elif (value < 0.5):
            colorsForEmotion.append("blue")
        elif (value < 0.7):
            colorsForEmotion.append("green")
        else:
            colorsForEmotion.append("orange")

    avgValence = totalValence / count
    toReturn = ""

    # output 
    if (avgValence < 0.3):
        toReturn += "Emotions associated with your music are very sad and gloomy. Your average valence is " + str(avgValence)
    elif (avgValence < 0.5):
        toReturn += "Emotions associated with your music are average, slightly on the sadder side. Your average valance is " + str(avgValence)
    elif (avgValence < 0.7):
        toReturn += "Emotions associated with your music are average, slightly on the happier side. Your average valance is " + str(avgValence)
    else:
        toReturn += "Emotions associated with your music are very happy and hype. Your average valance is " + str(avgValence)
    
    # putting data into the graph and displaying it
    fig = Figure()
    ax = fig.add_axes([0,0,1,1])
    ax.bar(songsForEmotion, graphHeight, color=colorsForEmotion)
    # ax.bar.set_title(toReturn + '\nEmotions of Your Music Depicted Through Colors')
    # ax.bar.set_xlabel(("Track # in Playlist"))

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    return render_template("image.html", image=pngImageB64String, text=toReturn)

app.run()
