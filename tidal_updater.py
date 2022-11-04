import os
import re
import json

import tidalapi


LOG_DIR = './logs/'


def __normalize(track):
    normalized = f"{track['name']} {track['artist']}".lower()
    normalized = re.sub(r'\s+', ' ', normalized)
    return normalized


def _filter_isrc_album(t_sp, t_td):
    return t_td.isrc == t_sp['isrc'] and t_td.album.name == t_sp['album']


def _filter_isrc(t_sp, t_td):
    return t_td.isrc == t_sp['isrc']


def _filter_title_artist_album(t_sp, t_td):
    return t_td.name == t_sp['name'] and t_td.artist.name == t_sp['artist'] and t_td.album.name == t_sp['album']


def _filter_title_artist(t_sp, t_td):
    return t_td.name == t_sp['name'] and t_td.artist.name == t_sp['artist']


_FILTERS_ALBUM = [
    _filter_isrc_album,
    _filter_isrc,
    _filter_title_artist_album,
    _filter_title_artist
]

_FILTERS = [
    _filter_isrc,
    _filter_title_artist
]


def search_track(session, track, filter_album=True):
    query = __normalize(track)
    res = session.search(query, models=[tidalapi.Track])
    tidal_track = None

    for _filter in (_FILTERS_ALBUM if filter_album else _FILTERS):
        try:
            tidal_track = next(t for t in res['tracks'] if _filter(track, t))
        except Exception:
            pass

        if tidal_track is not None:
            break

    return tidal_track


def manual_search(session, track, max_options=5):
    query = __normalize(track)
    res = session.search(query, models=[tidalapi.Track])

    if len(res['tracks']) == 0:
        return None

    options = min(len(res['tracks']), max_options)

    print('-' * 20)
    print(f'Which one is "{track["name"]} - {track["artist"]} ({track["album"]})"?')
    print('\n'.join([
        f'{j + 1}: {t.name} - {t.artist.name} ({t.album.name})' for j, t in enumerate(res['tracks'][:options])
    ]))
    number = input(f'Choose a number? [1-{options}]')

    try:
        return res['tracks'][int(number.strip()) - 1]
    except Exception:
        return None


def add_tracks_to_playlist(session, playlist, tracks, search_for_duplicates=True, _manual=False):
    print('Searching tracks in Tidal.')
    tracks_in = set([t.isrc for t in playlist.tracks()]) if search_for_duplicates else []

    t_ids = []
    skipped_tracks = []
    not_found_tracks = []
    added_tracks = []
    for track in tracks:
        if track['isrc'] in tracks_in:
            skipped_tracks.append(track)
            continue

        tidal_track = search_track(session, track) if not _manual else manual_search(session, track)
        if tidal_track is None:
            not_found_tracks.append(track)
            continue

        added_tracks.append(track)
        t_ids.append(tidal_track.id)

        if len(t_ids) == 100:
            # tidal api has a limit of 100 ids per request, so split the list
            print('Adding 100 items...')
            playlist.add(t_ids)
            del t_ids
            t_ids = []

    print('Adding the last items.')
    if len(t_ids) > 0:
        playlist.add(t_ids)

    data = {
        'skipped': skipped_tracks,
        'not_found': not_found_tracks,
        'added': added_tracks
    }

    print('Summary:', end=' ')
    print(','.join([f'{k}: {len(v)}' for k, v in data.items()]))

    if len(not_found_tracks) > 0:
        y0n = input('Some tracks could not be found, do you want to try manually? [Y/n] ')

        if y0n.lower() in ['1', 'y', 'yes']:
            _data = add_tracks_to_playlist(
                session, playlist, not_found_tracks,
                search_for_duplicates=search_for_duplicates,
                _manual=True)

            for k, v in _data.items():
                data[k].extend(v)

    os.makedirs(LOG_DIR, exist_ok=True)

    with open(os.path.join(LOG_DIR, f'{playlist.name}.json'), 'w') as f:
        json.dump(data, f)

    return data
