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
def get_last_index_with_bpm_data(csv_file_path):
    df = pd.read_csv(csv_file_path)
    # Iterate over the DataFrame in reverse order
    most_recent_index = 0
    for index, row in df.iterrows():
        if pd.notna(row['bpm']):
            most_recent_index = index
        else:
            break
    # return 123000
    return most_recent_index

# Helper function
def get_track_urls(df, start_index, end_index):
    track_urls = []
    for index in range(start_index, end_index):
        row = df.iloc[index]
        url = row['uri']
        track_urls.append(url)
    return track_urls

# BE CAREFUL: A mock function to be used for testing this script without API
def _mock_get_track_info(track_urls, retries=3):
    return [{'artist_genres': ['pop'], 'bpm': 100, 'explicit': True, 'duration_ms': 10000} for
            track_url in track_urls]

# This function takes in an array of spotify track urls, and returns a corresponding array of
# dictionaries (each dictionary contains a list of a genres, a bpm, an explicit rating,
# and a duration).
def _get_track_info(uris, retries=3):
    track_ids = [uri.split(":")[2] for uri in uris]
    track_info_cache = {}
    for _ in range(retries):
        try:
            # Get track information
            track_infos = sp.tracks(track_ids)['tracks']
            # artist_ids = [track_info['artists'][0]['id'] for track_info in track_infos]
            # artist_ids = list(artist_ids)
            # artist_infos = sp.artists(artist_ids)['artists']
            
            for track_info in track_infos:
                track_id = track_info['id']
                # genres = artist_info['genres']
                bpm = sp.audio_features([track_id])[0]['tempo']
                
                song_info = {
                    # 'artist_genres': genres,
                    'bpm': bpm,
                    'explicit': track_info['explicit'],
                    'duration_ms': track_info['duration_ms']
                }
                track_info_cache[track_id] = song_info
            break  # Break out of the retry loop if successful
        except Exception as e:
            print(f"Error processing tracks: {str(e)}")
            print("Sleeping for 5 seconds before retry...")
            time.sleep(5)
            if retries > 0:
                retries -= 1
                print(f"Retrying... ({retries} retries left)")
                time.sleep(5)  # Add a delay before retrying

    return [track_info_cache[track_id] for track_id in track_ids]

# The main function that we call. Continually updates the provided csv file by fetching
# genre/bpm/explicit/duration info from Spotify API
def update_csv(csv_file_path, starting_row_index=0):
    # Read the input CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)

    # Iterate over the DataFrame in batches
    start_index = starting_row_index
    batch_size = 50  # Adjust as needed
    current_count = 0
    while start_index < len(df):
        print("Current row index: {}...".format(start_index))
        time.sleep(3)
        end_index = min(start_index + batch_size, len(df))
        track_urls = get_track_urls(df, start_index, end_index)
        
        # Fetch track info for the batch of track URLs
        track_infos = _get_track_info(track_urls)
        
        # Update DataFrame with fetched track info
        for index in range(start_index, end_index):
            row = df.iloc[index]
            track_info = track_infos[index - start_index]  # Adjust index for batch
            df.at[index, 'artist_id'] = track_info['artist']
            df.at[index, 'bpm'] = track_info['bpm']
            df.at[index, 'explicit'] = track_info['explicit']
            df.at[index, 'duration_ms'] = track_info['duration_ms']

        current_count += batch_size

        # After every 1000 songs, save progress and update start_index
        if current_count >= 200:
            print("Saving progress to output file...")
            df.to_csv(csv_file_path, index=False)
            current_count = 0

        start_index = end_index

    # Save the final DataFrame
    df.to_csv(csv_file_path, index=False)


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
parser = argparse.ArgumentParser(description='This script can be used to add bpm/duration/explicit information to our dataset.')

# Add arguments
parser.add_argument('charts_csv_file_path', type=str, help='Input charts CSV file path')
# parser.add_argument('artists_csv_file_path', type=str, help='Artist information CSV file path')
parser.add_argument('output_csv_file_path', type=str, help='Output CSV file path')
parser.add_argument('-d', '--delete-existing-output-file', action='store_true', help='Whether to delete an existing output file and start over.')

# Parse arguments
args = parser.parse_args()

# Some sanity checks...
if args.charts_csv_file_path == args.output_csv_file_path:
    raise Error("Input CSV file path shouldn't be the same as output CSV file path!")
if args.delete_existing_output_file and os.path.exists(args.output_csv_file_path):
    should_continue = ask_yes_no_question("Are you sure you want to delete the existing output file and create a new one?")
    if should_continue:
        print("Deleting existing output file...")
        os.remove(args.output_csv_file_path)
    else:
        exit("Stopping script...")


current_index = 0
if os.path.exists(args.output_csv_file_path):
    print("Finding the most recent row index for which we already have genre/bpm/explicit/duration info...")
    current_index = get_last_index_with_bpm_data(args.output_csv_file_path) + 1
    print("Most recent index is {}!".format(current_index))
else:
    print("Creating initial output file by copying input file and adding new columns...")
    df = pd.read_csv(args.charts_csv_file_path)
    # df['genres'] = None
    df['bpm'] = None
    df['explicit'] = None
    df['duration_ms'] = None
    df.to_csv(args.output_csv_file_path, index=False)


update_csv(args.output_csv_file_path, starting_row_index=current_index)
