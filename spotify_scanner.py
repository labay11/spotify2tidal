import os
import json


DIR_PLAYLISTS = './playlists/'


def get_user_playlists_dir(user):
    path = os.path.join(DIR_PLAYLISTS, user)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def get_user_playlists_file(user):
    return os.path.join(get_user_playlists_dir(user), 'playlists.json')


def get_user_playlist_tracks_file(user, playlist_id):
    return os.path.join(get_user_playlists_dir(user), f'{playlist_id}.json')


def save_user_playlists_file(user, playlists):
    with open(get_user_playlists_file(user), 'w') as f:
        json.dump(playlists, f)
    return playlists


def save_user_playlists_tracks(user, playlist_id, tracks):
    with open(get_user_playlist_tracks_file(user, playlist_id), 'w') as f:
        json.dump(tracks, f)
    return tracks


def load_tracks_from_playlist(sp, user, playlist_id):
    if os.path.exists(get_user_playlist_tracks_file(user, playlist_id)):
        data = None
        with open(get_user_playlist_tracks_file(user, playlist_id), 'r') as f:
            data = json.load(f)
        return data

    print('Getting tracks from Spotify.')

    offset = 0
    limit = 100
    songs = []

    while True:
        content = sp.user_playlist_tracks(user, playlist_id, fields=None, limit=limit, offset=offset, market=None)
        songs.extend([
            {
                'id': s['track']['id'],
                'isrc': s['track']["external_ids"]["isrc"],
                'name': s['track']['name'],
                'artist': s['track']["artists"][0]['name'],
                'album': s['track']['album']['name']
            } for s in content['items']
            # track information might be empty (#1)
            if s['track'] is not None and 'isrc' in s['track']["external_ids"]
        ])

        if content['next'] is not None:
            offset += limit
        else:
            break

    return save_user_playlists_tracks(user, playlist_id, songs)


def load_user_playlists(sp, user):
    if os.path.exists(get_user_playlists_file(user)):
        data = None
        with open(get_user_playlists_file(user), 'r') as f:
            data = json.load(f)
        return data

    to_save = []
    playlists = sp.user_playlists(user)

    while playlists:
        for p in playlists['items']:
            if p['tracks']['total'] > 0:
                to_save.append({
                    'id': p['id'],
                    'name': p['name'],
                    'description': p['description'],
                    'owner': p['owner']['id'],
                    'tracks': p['tracks']['total'],
                    'uri': p['uri']
                })

        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    return save_user_playlists_file(user, to_save)
