import os
import sys

from spotify import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from spotify_scanner import load_tracks_from_playlist, load_user_playlists

from tidalapi import Session
from tidal_updater import add_tracks_to_playlist

CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID") or ""
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET") or ""


def is_yes(yOn):
    return yOn.lower() in ['1', 'y', 'yes', 'si', 's']


def playlist_selector(playlists, print_names=True):
    print('-' * 50)

    if print_names:
        print('\n'.join([f'{j + 1}: {p["name"]} ({p["tracks"]})' for j, p in enumerate(playlists)]))
        print('-' * 50)

    idxs = input('Which playlist do you want to import? (comma separated or 0 for all)')

    try:
        idxs = set(map(int, [s.strip() for s in idxs.split(',')]))
    except Exception:
        print('Invalid input, enter a comma-separated list of indices.')
        playlist_selector(playlists, print_names=False)

    if 0 in idxs:
        return playlists

    return [playlists[j - 1] for j in idxs]


def run_conversion(sp, spotify_user, tidal):
    playlists = load_user_playlists(sp, spotify_user)
    playlists = playlist_selector(playlists)

    if not playlists:
        print('No playlist selected')
        return 0

    print(f'Starting import of {len(playlists)} playlists.')

    tidal_playlists = tidal.user.playlists()

    for playlist in playlists:
        print(f'Importing tracks from {playlist["name"]}')
        # check if a playlist with the same name already exists in TIDAL
        exisiting_playlists = [p for p in tidal_playlists if playlist['name'] == p.name]
        if len(exisiting_playlists) > 0:
            yOn = input(f'Playlist "{playlist["name"]}" already exists, do you want to create a copy? [Y/n] ')

            if is_yes(yOn):
                # create a new one with a modified name
                tidal_playlist = tidal.user.create_playlist(playlist['name'] + ' (spotify)', playlist['description'])
            else:
                # Insert into the same playlist
                tidal_playlist = exisiting_playlists[0]
        else:
            # create a new playlist with the same name
            tidal_playlist = tidal.user.create_playlist(playlist['name'], playlist['description'])

        # get all spotify tracks
        tracks = load_tracks_from_playlist(sp, spotify_user, playlist['id'])
        # add the tracks to TIDAL
        add_tracks_to_playlist(tidal, tidal_playlist, tracks)

    return len(playlists)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Include spotify user name.")
        os.exit(1)

    print('Connecting to Spotify...', end='')
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = Spotify(client_credentials_manager=auth_manager)
    print('OK')

    print('Connecting to TIDAL...')
    tidal = Session()
    tidal.login_oauth_simple()
    print('OK')

    while True:
        run_conversion(sp, sys.argv[1], tidal)
        yOn = input('\n Do you want to continue? [Y/n] ')
        if not is_yes(yOn):
            break
