"""
Created by Tao Le Minh
"""

from dotenv import load_dotenv
import pandas as pd
import os
import base64
from requests import post, get
import json
from datetime import datetime as dt

load_dotenv()
client_id = os.getenv("SPOTIPY_CLIENT_ID")
client_secret = os.getenv("SPOTIPY_CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    header = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=header, data=data)

    return json.loads(result.content)['access_token']

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def get_current_user_profile(token):
    url = "https://api.spotify.com/v1/me"
    header = get_auth_header(token)
    result = get(url, headers=header)
    json_result = json.loads(result.content)

    return json_result

def search_for_artist_id(token, artist_name):
    """
    return artist_id of the first search result
    """
    url = "https://api.spotify.com/v1/search"
    header = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=5"
    query_url = url + "?" + query
    result = get(query_url, headers=header)

    json_result = json.loads(result.content)['artists']["items"][0]['id']

    return json_result

def search_for_artist_name(token, artist_name):
    """
    return artist_id of the first search result
    """
    url = "https://api.spotify.com/v1/search"
    header = get_auth_header(token)
    query = f"q={artist_name}&type=artist&limit=3"
    query_url = url + "?" + query
    result = get(query_url, headers=header)

    json_result = json.loads(result.content)['artists']["items"][0]['name']

    return json_result

def get_top_tracks_by_artist(token, artist_id):
    """
    return top 10 songs of an artist, calculated by Spotify
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=VN"
    header = get_auth_header(token)
    result = get(url, headers=header)
    track = json.loads(result.content)['tracks']

    top10 = {}
    for i in range(len(track)):
        top10[i] = {}
        cur_song = track[i]
        top10[i]['track_name'] = cur_song['name']
        top10[i]['album'] = cur_song['album']['name']
        top10[i]['release_date'] = cur_song['album']['release_date']
        top10[i]['artist'] = [i['name'] for i in cur_song['artists']]
        total_sec = int(cur_song['duration_ms'] / 1000)
        sec = total_sec % 60
        min = total_sec // 60
        top10[i]['duration'] = f"{min}:{str(sec).zfill(2)}"
        top10[i]['popularity'] = cur_song['popularity']

    df = pd.DataFrame.from_dict(top10, orient='index')
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year

    return df

def number_albums_of_artist(token, artist_id):
    limit = 50
    offset = 0
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&limit={limit}&offset={offset}"
    result = get(url, headers=header)
    total= json.loads(result.content)['total']

    return total
    

def number_singles_of_artist(token, artist_id):
    limit = 50
    offset = 0
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=single&limit={limit}&offset={offset}"
    result = get(url, headers=header)
    total = json.loads(result.content)['total']

    return total

def get_all_albums_by_artist(token, artist_id):
    """
    return all the albums, including albums, singles, compliations of an artist
    """
    limit = 50
    offset = 0
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single,compilation&limit={limit}&offset={offset}"
    result = get(url, headers=header)
    album = []
    total= json.loads(result.content)['total']
    while offset <= total:
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single,compilation&limit={limit}&offset={offset}"
        result = get(url, headers=header)
        for i in json.loads(result.content)['items']:
            album.append(i)
        offset += limit

    albumlist = {}
    for i in range(len(album)):
        albumlist [f"album{i}"] = {}
        cur_album = album[i]
        albumlist[f"album{i}"]['name'] = cur_album["name"]
        albumlist[f"album{i}"]['type'] = cur_album["album_type"]
        albumlist[f"album{i}"]['id'] = cur_album["id"]
        albumlist[f"album{i}"]['release_date'] = cur_album["release_date"]
        albumlist[f"album{i}"]['total_tracks'] = cur_album["total_tracks"]

    df = pd.DataFrame.from_dict(albumlist, orient='index')
    df['release_date'] = pd.to_datetime(df['release_date'])
    df['release_year'] = df['release_date'].dt.year

    return df

def get_all_album_id_by_artist(token, artist_id):
    """
    return all the album_id of the artist, including albums, singles, compliations
    """
    limit = 50
    offset = 0
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single,compilation&limit={limit}&offset={offset}"
    result = get(url, headers=header)
    album = []
    total= json.loads(result.content)['total']
    while offset <= total:
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album,single,compilation&limit={limit}&offset={offset}"
        result = get(url, headers=header)
        for i in json.loads(result.content)['items']:
            album.append(i)
        offset += limit

    album_id_list = []
    for i in range(len(album)):
        cur_album = album[i]
        album_id_list.append(cur_album["id"])

    return album_id_list

def get_albums(token, album_id):
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/albums/{album_id}"
    result = get(url, headers=header)

    return json.loads(result.content)

def get_tracks(token, track_id):
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    result = get(url, headers=header)

    return json.loads(result.content)

def get_tracks_by_album(token, album_id, output_type='df'):
    """
    return all the tracks of an album
    """
    limit = 50
    offset = 0
    album = get_albums(token, album_id)
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}"
    result = get(url, headers=header)
    total = json.loads(result.content)['total']
    track_list = []

    while offset <= total:
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}"
        result = get(url, headers=header)
        for i in json.loads(result.content)['items']:
            track_list.append(i)
        offset += limit

    track_dict = {}
    for i in range(len(track_list)):
        track_dict[i] = {}
        cur_song = track_list[i]
        track_dict[i]['track_name'] = cur_song['name']
        track_dict[i]['album'] = album['name']
        track_dict[i]['artist'] = [i['name'] for i in cur_song['artists']]
        track_dict[i]['uri'] = cur_song['uri']
        total_sec = int(cur_song['duration_ms'] / 1000)
        sec = total_sec % 60
        min = total_sec // 60
        track_dict[i]['duration'] = f"{min}:{str(sec).zfill(2)}"
        track_dict[i]['popularity'] = get_tracks(token, cur_song['id'])['popularity']
        # track_dict[i]['release_date'] = dt.strptime(album['release_date'], '%Y-%m-%d').date()
        track_dict[i]['release_date'] = album['release_date']
        # track_dict[i]['release_year'] = track_dict[i]['release_date'].year

    if output_type == 'json':
        return track_dict
    else:
        return pd.DataFrame.from_dict(track_dict, orient='index')
    
def get_track_id_by_album(token, album_id):
    """
    return the track_id of all the album tracks
    """
    limit = 50
    offset = 0
    album = get_albums(token, album_id)
    header = get_auth_header(token)
    url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}"
    result = get(url, headers=header)
    total = json.loads(result.content)['total']
    track_list = []

    while offset <= total:
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit={limit}&offset={offset}"
        result = get(url, headers=header)
        for i in json.loads(result.content)['items']:
            track_list.append(i)
        offset += limit

    track_id_list = []
    for i in range(len(track_list)):
        cur_song = track_list[i]
        track_id_list.append(cur_song['uri'])

    return track_id_list

def get_tracks_by_artist(token, artist_id, output_type='df'):
    """
    return all the tracks available on Spotify by an artist
    """
    album_id_list = get_all_album_id_by_artist(token, artist_id)

    tracks_df = pd.DataFrame()
    for alid in album_id_list:
        tracks_df = pd.concat([tracks_df, get_tracks_by_album(token, alid)], ignore_index=True)
    return tracks_df

def get_track_id_by_artist(token, artist_id):
    """
    return the track_id of all the artist tracks
    """
    album_id_list = get_all_album_id_by_artist(token, artist_id)
    track_id_set = set()

    for i in album_id_list:
        track_id_set.update(get_track_id_by_album(token, i))
    return track_id_set