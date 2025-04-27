import streamlit as st
import requests
import base64
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import os
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
from textblob import TextBlob

# Obtener client_id y client_secret desde las variables de entorno
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

if not client_id or not client_secret:
    raise ValueError("No se pudo encontrar client_id o client_secret en las variables de entorno.")

# Función para obtener el token de Spotify
def get_spotify_token(client_id, client_secret):
    auth_string = f"{client_id}:{client_secret}"
    b64_auth_string = base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')
    
    headers = {
        "Authorization": f"Basic {b64_auth_string}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    token = response.json().get('access_token')
    return token

# Función para obtener los álbumes de un artista desde Spotify
def get_spotify_albums(artist_name, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    search_url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    response = requests.get(search_url, headers=headers)
    artist_data = response.json()
    artist_id = artist_data['artists']['items'][0]['id']
    
    albums_url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album&limit=50"
    response = requests.get(albums_url, headers=headers)
    albums_data = response.json()
    
    albums = []
    for album in albums_data['items']:
        albums.append({'name': album['name'], 'release_date': album['release_date'], 'id': album['id']})
    
    return albums

# Función para obtener las canciones de un álbum
def get_album_tracks(album_id, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    tracks_url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
    response = requests.get(tracks_url, headers=headers)
    tracks_data = response.json()
    
    tracks = []
    for track in tracks_data['items']:
        tracks.append({'name': track['name'], 'track_number': track['track_number']})
    
    return tracks

# Función para obtener los álbumes de estudio desde Wikipedia
def get_studio_albums_from_wikipedia(artist_name):
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={artist_name} discography"
    response = requests.get(search_url)
    data = response.json()
    
    if 'query' in data:
        page_title = data['query']['search'][0]['title']
        wikipedia_url = f"https://en.wikipedia.org/wiki/{page_title}"
        response = requests.get(wikipedia_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        studio_albums_section = soup.find('th', class_='navbox-group', string='Studio albums')
        
        if studio_albums_section:
            albums_list = studio_albums_section.find_next('ul')
            albums = []
            for item in albums_list.find_all('li'):
                album_name = item.find('i').text if item.find('i') else item.text
                album_link = "https://en.wikipedia.org" + item.find('a')['href'] if item.find('a') else ''
                albums.append({'Title': album_name, 'Link': album_link})
            return albums
    return []

# Función para obtener las letras de las canciones
def get_lyrics(song_title):
    url = f"https://api.lyrics.ovh/v1/{artist_name}/{song_title}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('lyrics', 'No lyrics found')
    else:
        return 'No lyrics found'
    
# Visualización de la frecuencia de palabras
def plot_word_frequency(word_freq):
    most_common_words = word_freq.most_common(10)
    words, counts = zip(*most_common_words)

    fig = px.bar(x=words, y=counts, labels={'x': 'Word', 'y': 'Frequency'},
                 title="Most Frequent Words in Lyrics")
    st.plotly_chart(fig)

# Análisis de las letras: Longitud de las canciones y frecuencia de palabras
def analyze_lyrics(lyrics):
    song_length = len(lyrics.split())  # Longitud de la canción en palabras
    words = lyrics.lower().split()  # Lista de palabras en la letra
    word_freq = Counter(words)  # Contar frecuencia de palabras

    return song_length, word_freq

# Visualización de la palabra más frecuente usando WordCloud
def plot_wordcloud(word_freq):
    wordcloud = WordCloud(background_color='white',width=800, height=400).generate_from_frequencies(word_freq)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    st.pyplot(plt)

# Visualización de análisis de sentimiento de la letra de la canción
def plot_sentiment(lyrics):
    blob = TextBlob(lyrics)
    sentiment = blob.sentiment.polarity  # Valor de sentimiento entre -1 (negativo) y 1 (positivo)

    sentiment_label = 'Positive' if sentiment > 0 else 'Negative' if sentiment < 0 else 'Neutral'
    sentiment_color = 'green' if sentiment > 0 else 'red' if sentiment < 0 else 'gray'

    fig, ax = plt.subplots(figsize=(6, 2))
    ax.barh([0], [sentiment], color=sentiment_color)
    ax.set_xlim(-1, 1)
    ax.set_yticks([])
    ax.set_title(f'Sentiment: {sentiment_label}')
    st.pyplot(fig)

# Aplicación Streamlit
st.title("Explorador de Discografía de Artistas y Letras de Canciones")

# Inputs del usuario
artist_name = st.text_input("Introduce el nombre del artista o banda:")

if artist_name:
    token = get_spotify_token(client_id, client_secret)
    
    # Obtener los álbumes de Spotify
    albums = get_spotify_albums(artist_name, token)
    
    # Obtener los álbumes de estudio desde Wikipedia
    wikipedia_albums = get_studio_albums_from_wikipedia(artist_name)
    
    # Filtrar los álbumes para que solo aparezcan los de estudio que coinciden con los de Spotify
    studio_album_names = [album['Title'] for album in wikipedia_albums]
    filtered_albums = [album for album in albums if album['name'] in studio_album_names]
    
    # Mostrar los álbumes en Streamlit
    album_names = [album['name'] for album in filtered_albums]
    selected_album_name = st.selectbox("Selecciona un álbum:", album_names)
    
    selected_album = next(album for album in filtered_albums if album['name'] == selected_album_name)
    tracks = get_album_tracks(selected_album['id'], token)
    
    # Mostrar las canciones del álbum seleccionado
    track_names = [track['name'] for track in tracks]
    selected_song_name = st.selectbox("Selecciona una canción:", track_names)
    
    selected_song = next(track for track in tracks if track['name'] == selected_song_name)
    
    # Obtener las letras de la canción seleccionada
    lyrics = get_lyrics(selected_song['name'])
    st.write("Letras de la canción:")
    st.text_area("Letras", lyrics, height=300)
    
    # Mostrar análisis de las letras de la canción
    st.write("Análisis de las letras de la canción:")
    
    song_length, word_freq = analyze_lyrics(lyrics)

    st.write(f"Longitud de la canción (en palabras): {song_length}")

    st.subheader("Frecuencia de palabras")
    plot_word_frequency(word_freq)
                        
    st.subheader("Nube de palabras")
    plot_wordcloud(word_freq)
                        
    st.subheader("Análisis de Sentimiento")
    plot_sentiment(lyrics)
