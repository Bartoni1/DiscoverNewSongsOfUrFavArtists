import json
import requests
import tekore as tk
import random
from spotipy.oauth2 import SpotifyClientCredentials

file = open('secrets.txt','r')

SECRETS = []
for secret in file.readlines():
    secret = secret.rstrip()
    SECRETS.append(str(secret))

SCOPE = 'playlist-read-private playlist-read-public'
CLIENT_ID = SECRETS[0]
USER_SECRET = SECRETS[1]
REDIRECT_URI = SECRETS[2]
REHRESH_TOKEN = SECRETS[3]
TOKEN = tk.RefreshingCredentials(client_id = CLIENT_ID, client_secret=USER_SECRET, redirect_uri=REDIRECT_URI, sender=None).refresh_user_token(REHRESH_TOKEN)

def main():
    print("You should know that limit of playlist we can get is 50, so keep in mind some of your older playlists can't be detected!")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN)
    }

    r = requests.get('https://api.spotify.com/v1/me/playlists?limit=50&offset=0', headers=headers)
    
    data = r.json()
    
    while True:
        user_input = input("Give playlist name\n")
        loop_bool = False
        for i in range(0, len(data['items'])):
            
            if str(data['items'][i]['name']) == str(user_input):
                print("-----------------------------------------------------")
                print("Playlist chosen succesfully!")
                print("-----------------------------------------------------")
                
                chosen_playlist = data['items'][i]
                chosen_playlist_name = str(data['items'][i]['name'])
                chosen_playlist_id = chosen_playlist['id']
                
                total_songs = int(data['items'][i]['tracks']['total'])
                
                user_id = str(data['href']).replace('https://api.spotify.com/v1/users/', '')
                user_id = user_id.replace('/playlists?offset=0&limit=50', '')
                
                loop_bool = True
                
        if loop_bool:
            break
        else:
            print("-----------------------------------------------------")
            print("Playlist name not in data!")
            print("-----------------------------------------------------")
    
    print("\nCreating playlist & adding tracks...")
    
    artist_ids = []
    
    
    for i in range(0, total_songs, 50):
        request = requests.get("https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=50&offset={i}".format(playlist_id=chosen_playlist_id, i = i), headers= headers)
            
        data2 = request.json()
        for item in data2['items']:
            artist_url = item['track']['album']['artists'][0]['external_urls']
            artist_id = str(artist_url['spotify']).replace('https://open.spotify.com/artist/', '')
            artist_ids.append(artist_id)
    
    markets = requests.get('https://api.spotify.com/v1/markets', headers=headers).json()
    markets = markets['markets']

    track_ids = []

    for id in artist_ids:
        randomize_market = random.randint(0, len(markets) - 1)
        
        market = markets[randomize_market]
        
        rqst = requests.get("https://api.spotify.com/v1/artists/{id}/top-tracks?market={market}".format(market=market, id=id), headers = headers)
    
        data3 = rqst.json()
        
        randomize_track =  random.randint(0, len(data3['tracks']) - 1)
        
        track_id = data3['tracks'][randomize_track]['id']
        
        track_ids.append(track_id)
        
    
    headers2= { 
        "Content-Type": "application/json",
        "Authorization": "Bearer {token}".format(token=TOKEN),    
    }
    
    r2 = requests.post('https://api.spotify.com/v1/users/{user_id}/playlists'.format(user_id = user_id), headers=headers2, data ="{\"name\":\"Playlist created automatically\",\"public\":false}")
    
    created_playlist = r2.json()
    
    created_playlist_id = created_playlist['id']
    
    track_uris = []
    
    for track_id in track_ids:
        track_uris.append("spotify:track:" + str(track_id))

    for track_uri in track_uris:
        data_add_to_playlist = {
        "uris": [
            str(track_uri)
        ]
        }
        r5 = requests.post('https://api.spotify.com/v1/playlists/{playlist_id}/tracks?uris={uri}'.format(playlist_id = created_playlist_id, uri = str(track_uri)), headers=headers, data=data_add_to_playlist)
    print("\nProcess completed\n")
    
if __name__ == "__main__":  
    main()
