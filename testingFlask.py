from flask import Flask, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return ''' <label for="url">Playlist URL:</label>
    <input type="text" id="url"><br><br>
    <button onClick=window.location.replace('http://127.0.0.1:5000/bruh?url='+document.getElementById('url').value)>Click Me!</button> '''

@app.route("/bruh")
def bruh():
    r = request.values.get('url')
    return f"<p>{r}</p>"

app.run()
