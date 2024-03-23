# import pandas as pd

# # List of file paths
# file_paths = ['combined_germany.csv', 'combined_global.csv', 'combined_india.csv', 'combined_usa.csv']

# # Initialize an empty list to store DataFrames
# dfs = []

# # Loop through each file path, read the CSV, and append to dfs list
# for file_path in file_paths:
#     df = pd.read_csv(file_path)
#     dfs.append(df)

# # Concatenate all DataFrames in dfs list into a single DataFrame
# combined_df = pd.concat(dfs, ignore_index=True)

# # Optionally, you can save the combined DataFrame to a new CSV file
# combined_df.to_csv('combined_data.csv', index=False)


import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('combined_data.csv')

# Find unique URLs
unique_urls = df['uri'].unique()

# Convert the unique URLs to a DataFrame
unique_urls_df = pd.DataFrame(unique_urls, columns=['uri'])

# Save the unique URLs DataFrame to a new CSV file
unique_urls_df.to_csv('uris.csv', index=False)