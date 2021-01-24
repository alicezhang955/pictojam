from flask import Flask, request, redirect, g, render_template, session
from spotify_requests import spotify
import requests

app = Flask(__name__)
app.secret_key = 'some key for session'

@app.route('/')
def home():
    # Return the homepage
    return render_template('home.html')


@app.route('/playlists')
def playlists():
    # Show all playlists
    return render_template('playlists.html')


@app.route('/visualization')
def visualization():
    # Visualizing songs
    return render_template('visualization.html')


@app.route("/auth")
def auth():
    return redirect(spotify.AUTH_URL)


@app.route("/callback")
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header

    return profile()

@app.route('/profile')
def profile():
    if 'auth_header' in session:
        auth_header = session['auth_header']
        # get profile data
        profile_data = spotify.get_users_profile(auth_header)

        # get user playlist data
        playlist_data = spotify.get_users_playlists(auth_header)

        # get user recently played tracks
        recently_played = spotify.get_users_recently_played(auth_header)
        
        if valid_token(recently_played):
            return render_template("profile.html",
                               user=profile_data,
                               playlists=playlist_data["items"],
                               recently_played=recently_played["items"])

    return render_template('profile.html')

def valid_token(resp):
    return resp is not None and not 'error' in resp

@app.errorhandler(500)
def server_error(e):
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
