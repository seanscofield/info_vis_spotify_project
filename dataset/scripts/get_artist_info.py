###############
### IMPORTS ###
###############

import argparse
import os
import time

import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

########################
### USEFUL FUNCTIONS ###
########################

# Helper function
def ask_yes_no_question(prompt):
    while True:
        user_input = input(prompt + " (yes/no): ").strip().lower()
        if user_input in ('yes', 'no'):
            return user_input == 'yes'
        else:
            print("Please enter 'yes' or 'no'.")

# Helper function
def get_track_uris(df, start_index, end_index):
    track_uris = []
    for index in range(start_index, end_index):
        row = df.iloc[index]
        uri = row['uri']
        track_uris.append(uri)
    return track_uris

# This function takes in an array of spotify track uris, and returns an array of track objects
# from the Spotify API.
def get_several_tracks(track_uris, retries=3):
    if len(track_uris) > 50:
        raise Error("Not allowed to request more than 50 tracks at a time!")

    track_ids = [uri.split(":")[2] for uri in track_uris]
    for _ in range(retries):
        try:
            # Get track information
            return sp.tracks(track_ids)['tracks']

        except Exception as e:
            print(f"Error processing tracks: {str(e)}")
            print("Sleeping for 5 seconds before retry...")
            time.sleep(5)
            if retries > 0:
                retries -= 1
                print(f"Retrying... ({retries} retries left)")
                time.sleep(5)  # Add a delay before retrying



######################################
### SPOTIFY CLIENT AND GLOBAL VARS ###
######################################

# IMPORTANT: Make sure to set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars
if not os.getenv('SPOTIFY_CLIENT_ID') or not os.getenv('SPOTIFY_CLIENT_SECRET'):
    raise Error("Make sure to set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET env vars first!")

client_credentials_manager = SpotifyClientCredentials(client_id=os.getenv('SPOTIFY_CLIENT_ID'), client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


##########################
### RUNNING THE SCRIPT ###
##########################

# Create argument parser
parser = argparse.ArgumentParser(description='This script can be used to get artist genre information')

# Add arguments
parser.add_argument('input_csv_file_path', type=str, help='Input CSV file path')
parser.add_argument('output_csv_file_path', type=str, help='Output CSV file path')
parser.add_argument('-d', '--delete-existing-output-file', action='store_true', help='Whether to delete an existing output file and start over.')

# Parse arguments
args = parser.parse_args()

# Some sanity checks...
if args.input_csv_file_path == args.output_csv_file_path:
    raise Error("Input CSV file path shouldn't be the same as output CSV file path!")
if args.delete_existing_output_file and os.path.exists(args.output_csv_file_path):
    should_continue = ask_yes_no_question("Are you sure you want to delete the existing output file and create a new one?")
    if should_continue:
        print("Deleting existing output file...")
        os.remove(args.output_csv_file_path)
    else:
        exit("Stopping script...")


if os.path.exists(args.output_csv_file_path):
    raise Error("Output file already exists!")

df = pd.read_csv(args.input_csv_file_path)
artist_cache = {}

# Iterate over the DataFrame in batches
start_index = 0
batch_size = 15  # Adjust as needed
current_count = 0
while start_index < len(df):
    print("Current row index: {}...".format(start_index))
    time.sleep(1)
    end_index = min(start_index + batch_size, len(df))

    # Fetch track information first
    track_uris = get_track_uris(df, start_index, end_index)
    tracks = get_several_tracks(track_uris)

    # Fetch artist information (since 'genres' isn't there by default)
    artists = []
    for track in tracks:
        artists.extend(track['artists'])


    artist_ids = [artist['id'] for artist in artists]
    artist_ids = list(set(artist_ids))
    artist_infos = sp.artists(artist_ids)['artists']
    for artist in artist_infos:
        print(dict(id=artist['id'], name=artist['name'], genres=artist['genres']))
        artist_cache[artist['id']] = dict(id=artist['id'], name=artist['name'], genres=artist['genres'])
    start_index = end_index


data = [[artist['id'], artist['name'], ",".join(artist['genres'])] for artist in artist_cache.values()]
artists_df = pd.DataFrame(data, columns=['id','name','genres'])

artists_df.to_csv(args.output_csv_file_path, index=False)


