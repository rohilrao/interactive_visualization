import pandas as pd
import plotly.express as px
import streamlit as st

# Load the dataset
file_path = '../migration.csv'
df = pd.read_csv(file_path)

# Clean and preprocess the data with gender information
df.rename(columns=lambda x: x.split(' ')[0] if x.endswith(']') else x, inplace=True)
df = df[~df.isna().any(axis=1)]
df[['1960', '1970', '1980', '1990', '2000']] = df[['1960', '1970', '1980', '1990', '2000']].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
df['Total Migration'] = df[['1960', '1970', '1980', '1990', '2000']].sum(axis=1)

# Reshape the dataframe to a long format for plotting and analysis
long_df = df.melt(id_vars=['Country Origin Name', 'Country Dest Name', 'Migration by Gender Name'], 
                  value_vars=['1960', '1970', '1980', '1990', '2000'], 
                  var_name='Decade', 
                  value_name='Migration')

# Get top 5 migration corridors by decade and gender
top_5_corridors_gender = long_df.groupby(['Decade', 'Migration by Gender Name', 'Country Origin Name', 'Country Dest Name'])['Migration'].sum().reset_index()
top_5_corridors_gender = top_5_corridors_gender.sort_values(['Decade', 'Migration'], ascending=[True, False]).groupby(['Decade', 'Migration by Gender Name']).head(5)

# Get the top source country by decade and gender
top_source_country_gender = long_df.groupby(['Decade', 'Migration by Gender Name', 'Country Origin Name'])['Migration'].sum().reset_index()
top_source_country_gender = top_source_country_gender.sort_values(['Decade', 'Migration'], ascending=[True, False]).groupby(['Decade', 'Migration by Gender Name']).head(1)

# Get the top destination country by decade and gender
top_destination_country_gender = long_df.groupby(['Decade', 'Migration by Gender Name', 'Country Dest Name'])['Migration'].sum().reset_index()
top_destination_country_gender = top_destination_country_gender.sort_values(['Decade', 'Migration'], ascending=[True, False]).groupby(['Decade', 'Migration by Gender Name']).head(1)

# Streamlit App
st.title("Migration Analysis by Decade and Gender")

decade = st.selectbox('Select Decade:', ['All'] + [str(dec) for dec in sorted(top_5_corridors_gender['Decade'].unique())])
gender = st.selectbox('Select Gender:', ['All'] + sorted(top_5_corridors_gender['Migration by Gender Name'].unique()))
sort_order = st.radio('Sort Order:', ['Ascending', 'Descending'])

# Function to update the plot for top 5 migration corridors by decade and gender
def update_corridor_plot(decade, gender, sort_order):
    filtered_data = top_5_corridors_gender.copy()
    if decade != 'All':
        filtered_data = filtered_data[filtered_data['Decade'] == int(decade)]
    if gender != 'All':
        filtered_data = filtered_data[filtered_data['Migration by Gender Name'] == gender]
    
    sorted_data = filtered_data.sort_values(by='Migration', ascending=(sort_order == 'Ascending'))
    fig = px.bar(sorted_data, x='Country Origin Name', y='Migration', color='Country Dest Name',
                 title=f'Top 5 Migration Corridors in {decade} for {gender} (Sorted {sort_order})')
    st.plotly_chart(fig)

# Function to update the plot for top source country by decade and gender
def update_source_country_plot(decade, gender, sort_order):
    filtered_data = top_source_country_gender.copy()
    if decade != 'All':
        filtered_data = filtered_data[filtered_data['Decade'] == int(decade)]
    if gender != 'All':
        filtered_data = filtered_data[filtered_data['Migration by Gender Name'] == gender]
    
    sorted_data = filtered_data.sort_values(by='Migration', ascending=(sort_order == 'Ascending'))
    fig = px.bar(sorted_data, x='Country Origin Name', y='Migration',
                 title=f'Top Source Country in {decade} for {gender} (Sorted {sort_order})')
    st.plotly_chart(fig)

# Function to update the plot for top destination country by decade and gender
def update_destination_country_plot(decade, gender, sort_order):
    filtered_data = top_destination_country_gender.copy()
    if decade != 'All':
        filtered_data = filtered_data[filtered_data['Decade'] == int(decade)]
    if gender != 'All':
        filtered_data = filtered_data[filtered_data['Migration by Gender Name'] == gender]
    
    sorted_data = filtered_data.sort_values(by='Migration', ascending=(sort_order == 'Ascending'))
    fig = px.bar(sorted_data, x='Country Dest Name', y='Migration',
                 title=f'Top Destination Country in {decade} for {gender} (Sorted {sort_order})')
    st.plotly_chart(fig)

# Display plots based on user selection
st.header("Top 5 Migration Corridors")
update_corridor_plot(decade, gender, sort_order)

st.header("Top Source Country")
update_source_country_plot(decade, gender, sort_order)

st.header("Top Destination Country")
update_destination_country_plot(decade, gender, sort_order)
