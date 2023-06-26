import streamlit as st
import os
import base64
from requests import post, get
import json

# set up
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]

# load_dotenv()
# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_song(token, song, artist):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q=artist:{artist} track:{song}&type=track&limit=1"
    
    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)["tracks"]["items"]
    if len(json_result) == 0:
        print("No result...")
        return None
    return json_result[0]

def get_song_characteristics(token, track_id):
    url = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = get_auth_header(token)
    result = get(url=url, headers=headers)
    json_result = json.loads(result.content)
    return json_result


st.title(':blue[Spotify Song Characteristics]')

if 'token' not in st.session_state: st.session_state['token'] = get_token()
if 'song_id' not in st.session_state: st.session_state['song_id'] = []

input_container = st.container()
with input_container:
    with st.form(key = 'my_form', clear_on_submit = True):
            song_name = st.text_input("Enter song name", key = "song_name")
            artist_name = st.text_input("Enter artist name", key = "artist_name")
            submit_button = st.form_submit_button(label = 'search')

if submit_button and song_name and artist_name:
    song_search = search_for_song(token = st.session_state['token'],
                                  song = song_name,
                                  artist = artist_name)
    if song_search is not None:
        song_id = song_search["id"]
        st.session_state['song_id'].append(song_id)
        st.markdown(f"Retreived song ID is {song_id}")
        st.markdown(f"Retreived song name is {song_search['name']}")
        song_characteristics = get_song_characteristics(token = st.session_state['token'],
                                                        track_id = song_id)
        
        characteristics = ""
        for i, item in enumerate(song_characteristics):
            characteristics += f"{i + 1}. {item} : {song_characteristics[item]}\n"
        st.markdown(f"Here are the song characteristics:\n{characteristics}")
        uri = song_characteristics['uri'].split(":")[2]
        st.markdown(f"Review song at https://open.spotify.com/track/{uri}")
    else:
        st.markdown(f"API did not find a result.")
