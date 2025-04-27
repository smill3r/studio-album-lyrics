import streamlit as st
import wikipediaapi
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from collections import Counter
from wordcloud import WordCloud
from textblob import TextBlob

# Inicializar el objeto WikipediaAPI con un User-Agent personalizado
wiki_wiki = wikipediaapi.Wikipedia(
    language='en',
    user_agent='album-searcher'
)

# Función para obtener la URL de la discografía de un artista
def get_discography_url(artist_name):
    artist_name = artist_name.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{artist_name}_discography"
    return url

# Función para obtener los álbumes de estudio
def get_studio_albums(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    studio_albums_section = soup.find('th', class_='navbox-group', string='Studio albums')

    if studio_albums_section:
        albums_list = studio_albums_section.find_next('ul')
        albums = []
        for item in albums_list.find_all('li'):
            album_name = item.find('i').text if item.find('i') else item.text
            album_link = "https://en.wikipedia.org" + item.find('a')['href'] if item.find('a') else ''
            albums.append({'Title': album_name, 'Link': album_link})

        df_studio_albums = pd.DataFrame(albums)
        return df_studio_albums
    else:
        return None

# Función para obtener las canciones de un álbum
def get_album_songs(album_url):
    response = requests.get(album_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Intentar extraer las canciones de las tablas o listas del álbum
    songs = []
    # Buscar las listas o tablas de canciones en la página del álbum
    song_table = soup.find('table', {'class': 'tracklist'})

    if song_table:
        rows = song_table.find_all('tr')
        for row in rows:
            song = row.find('td')
            if song:
                song_name = song.get_text(strip=True)
                songs.append(song_name)

    # Si no hay canciones en formato tabla, intentamos en listas de enlaces
    if not songs:
        song_list = soup.find_all('ul')
        for ul in song_list:
            for li in ul.find_all('li'):
                song_name = li.get_text(strip=True)
                if song_name:
                    songs.append(song_name)

    return songs

# Función para buscar bandas en Wikipedia usando wikipedia-api
def search_bands(query):
    page = wiki_wiki.page(query)
    return page

# Función para obtener la letra de una canción
def get_song_lyrics(song_name, artist_name):
    url = f"https://api.lyrics.ovh/v1/{artist_name}/{song_name}"
    response = requests.get(url)

    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        try:
            data = response.json()
            # Verificar si se encontró la letra
            if 'lyrics' in data:
                return data['lyrics']
            else:
                st.error(f"No se encontraron letras para la canción: {song_name}")
                return None
        except ValueError:
            st.error("Hubo un error al procesar la respuesta de la API.")
            return None
    else:
        st.error(f"No se pudo obtener la letra de la canción: {song_name}. Código de respuesta: {response.status_code}")
        return None

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

# Visualización de la frecuencia de palabras
def plot_word_frequency(word_freq):
    most_common_words = word_freq.most_common(20)
    words, counts = zip(*most_common_words)

    fig = px.bar(x=words, y=counts, labels={'x': 'Word', 'y': 'Frequency'},
                 title="Most Frequent Words in Lyrics")
    st.plotly_chart(fig)

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

# Configuración de la aplicación
st.title('Explorador de Discografías de Artistas')

# Paso 1: Entrada de búsqueda
query = st.text_input("Escribe el nombre de un artista o banda:")

if query:
    # Paso 2: Buscar artistas relacionados
    result = search_bands(query)

    if result.exists():
        band_name = result.title
        st.write(f"Se ha encontrado la página de {band_name}")

        band_url = get_discography_url(band_name)

        if band_url:
            st.write(f"Buscando álbumes de estudio de {band_name}...")
            albums_df = get_studio_albums(band_url)

            if albums_df is not None:
                st.write(f"Álbumes de estudio de {band_name}:")
                st.dataframe(albums_df)

                # Paso 3: Elegir un álbum y explorar las canciones
                album = st.selectbox("Selecciona un álbum:", albums_df['Title'].tolist())

                # Obtener las canciones del álbum seleccionado
                album_url = albums_df[albums_df['Title'] == album]['Link'].values[0]
                songs = get_album_songs(album_url)

                if songs:
                    song = st.selectbox("Selecciona una canción:", songs)

                    lyrics = get_song_lyrics(song, band_name)

                    if lyrics:
                        st.write(f"Letras de {song}:")
                        st.text_area("Lyrics", lyrics, height=200)

                        # Análisis de letras
                        song_length, word_freq = analyze_lyrics(lyrics)
                        st.write(f"Longitud de la canción (en palabras): {song_length}")

                        # Gráficas
                        st.subheader("Frecuencia de palabras")
                        plot_word_frequency(word_freq)

                        st.subheader("Nube de palabras")
                        plot_wordcloud(word_freq)

                        st.subheader("Análisis de Sentimiento")
                        plot_sentiment(lyrics)

                else:
                    st.error("No se encontraron canciones para el álbum seleccionado.")
            else:
                st.error(f"No se pudo encontrar la sección de álbumes de estudio para {band_name}.")
        else:
            st.error("No se pudo generar la URL de la discografía.")
    else:
        st.error("No se encontraron resultados para la búsqueda.")
