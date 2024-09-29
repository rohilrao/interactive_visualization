import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import requests

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Function to query OpenAI API
def query_openai(api_key, image_base64, query_text):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": query_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

# Load the data
df = pd.read_csv('../migration.csv')

# Clean and preprocess the data
df.rename(columns=lambda x: x.split(' ')[0] if x.endswith(']') else x, inplace=True)
df = df[~df.isna().any(axis=1)]
df[['1960', '1970', '1980', '1990', '2000']] = df[['1960', '1970', '1980', '1990', '2000']].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
df['Total Migration'] = df[['1960', '1970', '1980', '1990', '2000']].sum(axis=1) #.astype(int)

# Reshape the dataframe to a long format for plotting
long_df = df.melt(id_vars=['Country Origin Name', 'Country Dest Name'], 
                  value_vars=['1960', '1970', '1980', '1990', '2000'], 
                  var_name='Decade', 
                  value_name='Migration')

# Get the top migration event for each decade
top_migrations = long_df.loc[long_df.groupby('Decade')['Migration'].idxmax()]

# Streamlit app
st.title('Migration Analysis')

# Plot 1: Primary source countries for migration
source_migration = df.groupby('Country Origin Name')['Total Migration'].sum().reset_index()
source_migration = source_migration.sort_values(by='Total Migration', ascending=False).head(5)

st.subheader('Top Source Countries for Migration')
fig1, ax1 = plt.subplots(figsize=(12, 6))
sns.barplot(x='Country Origin Name', y='Total Migration', data=source_migration, ax=ax1)
ax1.set_title('Top Source Countries for Migration')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
st.pyplot(fig1)

# Plot 2: Primary destination countries for migration
dest_migration = df.groupby('Country Dest Name')['Total Migration'].sum().reset_index()
dest_migration = dest_migration.sort_values(by='Total Migration', ascending=False).head(5)

st.subheader('Top Destination Countries for Migration')
fig2, ax2 = plt.subplots(figsize=(12, 6))
sns.barplot(x='Country Dest Name', y='Total Migration', data=dest_migration, ax=ax2)
ax2.set_title('Top Destination Countries for Migration')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
st.pyplot(fig2)

# Plot 3: Top migration events by decade
st.subheader('Top Migration Events by Decade')
fig3, ax3 = plt.subplots(figsize=(12, 8))

# Plotting the data
bars = ax3.bar(top_migrations['Decade'], top_migrations['Migration'], color='skyblue')

# Adding annotations with formatted numbers in millions
for bar, migration, origin, dest in zip(bars, top_migrations['Migration'], top_migrations['Country Origin Name'], top_migrations['Country Dest Name']):
    yval = bar.get_height()
    formatted_migration = f'{migration / 1e6:.1f}M'
    ax3.text(bar.get_x() + bar.get_width()/2, yval + 100000, f'{origin} to {dest}\n{formatted_migration}', ha='center', va='bottom', fontsize=10)

# Setting labels and title
ax3.set_xlabel('Decade')
ax3.set_ylabel('Number of Migrants')
ax3.set_title('Top Migration Events by Decade')
ax3.set_ylim(0, top_migrations['Migration'].max() * 1.1)

# Save the plot
plt.savefig('top_migration_events.png')

# Show the plot
st.pyplot(fig3)

# Input field for query
st.subheader('Query the Image')
api_key = st.text_input('Enter your OpenAI API Key')
query_text = st.text_input('Enter your query')

if st.button('Submit'):
    if api_key and query_text:
        # Encode the image and query the OpenAI API
        base64_image = encode_image('top_migration_events.png')
        response = query_openai(api_key, base64_image, query_text)
        st.write(response)
    else:
        st.write("Please enter both the API key and query text.")
