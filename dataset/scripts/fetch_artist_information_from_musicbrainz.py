import requests
import pandas as pd
import time


def get_artist_info(artist_name):
    # Set up the API endpoint
    base_url = "https://musicbrainz.org/ws/2/"
    endpoint = "artist"
    params = {
        "query": f'artist:"{artist_name}"',
        "fmt": "json"
    }
    response = requests.get(f"{base_url}{endpoint}", params=params)

    # Check if the request was successful
    if response.status_code == 200:
        # Extract artist information from the response
        data = response.json()
        if 'artists' in data and len(data['artists']) > 0:
            artist = data['artists'][0]
            artist_type = artist.get('type', 'Unknown')
            gender = artist.get('gender', None)
            return artist_type, gender
        else:
            return None, None
    else:
        print("Error fetching data from MusicBrainz API.")
        return None, None


def get_artist_information(artist_name):
    artist_info = get_artist_info(artist_name)
    artist_type, gender = artist_info

    # Determine whether the artist is a band or a solo act
    if artist_type == 'Person':
        artist_category = 'Solo Act'
    elif artist_type in ['Group', 'Band']:
        artist_category = 'Band'
    else:
        artist_category = 'Unknown'

    return gender, artist_category

# print(get_artist_information("SIRA"))

df = pd.read_csv('artists.csv')


artist_info = {}
starting_index = 0
count = 0
for index, row in df.iterrows():
    if index < starting_index:
        continue
    artist_name = row['name']  # Assuming 'Name' is the column containing artist names
    artist_id = row['id']
    # Do something with the artist data, for example:
    print("{}, Artist Name: {}".format(index, artist_name))
    res = get_artist_information(artist_name)
    gender, artist_category = res
    artist_info[artist_id] = dict(artist_name=artist_name, gender=gender, category=artist_category)
    print(gender, artist_category)
    count += 1
    if count % 20 == 0:
        data = [[artist_id, artist['artist_name'], artist['gender'], artist['category']] for artist_id, artist in artist_info.items()]
        artists_df = pd.DataFrame(data, columns=['artist_id','arist_name','gender','category'])
        artists_df.to_csv("artist_gender_and_category.csv", index=False)
    time.sleep(1)


data = [[artist_id, artist['artist_name'], artist['gender'], artist['category']] for artist_id, artist in artist_info.items()]
artists_df = pd.DataFrame(data, columns=['artist_id','arist_name','gender','category'])
artists_df.to_csv("artist_gender_and_category.csv", index=False)