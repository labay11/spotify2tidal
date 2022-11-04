# Spotify To Tidal

Even though TIDAL offers several services to import your Spotify playlist, all of them have a limit in the amount of
songs per playlist so their are not very useful if your playlist has more that 100 tracks.

This free and open source TIDAL playlist importer let's you convert all your Spotify playlist
with just one call of the script.

## Requirements

- [spotipy](https://github.com/spotipy-dev/spotipy)
- [tidalapi](https://github.com/tamland/python-tidal)

## Usage

1. Set the spotify client id and secret (either in an environment variable or directly in `importer.py`)
2. Run the importer with the spotify user name from where to retrieve the playlists

```python3
python3 importer.py [spotify-user-name]
```

3. Login to TIDAL using the link provided in the command line.
4. Select the playlist that you want to import.
5. Chill. Importing might take a while, let the computer work and rest listening to some music.
  - Some songs might fail to be found because TIDAL doesn't allow to search songs by their ISRC.
  In such case, you can use the manual selector to find the best possible match.
6. Enjoy

## LICENSE

   Copyright 2022 labay11

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
