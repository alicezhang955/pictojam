from flask import Blueprint
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.urls import url_parse

from flask import Flask, request, redirect, g, render_template, session
from app.spotify_requests import spotify
import requests


server_bp = Blueprint('main', __name__)

server_bp.secret_key = 'some key for session'

@server_bp.route('/')
def index():
    return render_template("home.html", title='Home Page')

@server_bp.route('/playlists')
def playlists():
    # Show all playlists
    return render_template('playlists.html')

@server_bp.route('/visualization')
def visualization():
    # Visualizing songs
    return render_template('visualization.html')

@server_bp.route('/auth')
def auth():
    return redirect(spotify.AUTH_URL)

@server_bp.route('/callback')
def callback():

    auth_token = request.args['code']
    auth_header = spotify.authorize(auth_token)
    session['auth_header'] = auth_header
    return profile()

@server_bp.route('/profile')
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

