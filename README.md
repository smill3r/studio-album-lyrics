# Explorador de Álbumes y Letras de Canciones

## Descripción del Proyecto

Este proyecto consiste en la creación de una aplicación web interactiva que permite explorar los álbumes y canciones de un artista o banda, obtener las letras de las canciones seleccionadas y realizar varios análisis de texto sobre las letras. La aplicación está construida utilizando Streamlit como framework web y hace uso de varias APIs externas para obtener la información relevante.

### Funcionalidades Principales
-	Búsqueda de Artistas: El usuario puede ingresar el nombre de un artista o banda y seleccionar un álbum de una lista generada dinámicamente a partir de la API de Spotify.
-	Selección de Canciones: Una vez seleccionado el álbum, el usuario puede elegir una canción para la cual se descargará la letra de la canción utilizando la API de Lyrics.ovh.
- Análisis de Sentimiento: Se realiza un análisis de sentimiento sobre la letra de la canción seleccionada usando TextBlob.
-	Generación de Nube de Palabras: Se genera una nube de palabras basada en la letra de la canción seleccionada, lo que permite visualizar las palabras más frecuentes de forma gráfica.
-	Frecuencia de Palabras: Se calcula la frecuencia de las palabras más comunes en la letra y se muestra un gráfico de barras con las 10 palabras más frecuentes.

### Tecnologías Utilizadas
-	Streamlit: Framework para la creación de aplicaciones web interactivas de forma rápida.
-	Spotify API: Para obtener información sobre los álbumes y canciones del artista.
-	Wikipedia API: Para filtrar los álbumes a solo aquellos considerados “álbumes de estudio”.
-	Lyrics.ovh API: Para obtener las letras de las canciones.
-	TextBlob: Librería de procesamiento de lenguaje natural para análisis de sentimientos.
-	WordCloud: Librería para la visualización de nubes de palabras a partir de texto.
-	Matplotlib: Para visualizar las gráficas generadas, como la nube de palabras y las frecuencias de palabras.

## Instrucciones de uso

### Variables de Entorno

El proyecto requiere las credenciales de la API de Spotify. Debes configurar las siguientes variables de entorno en tu sistema:
-	SPOTIFY_CLIENT_ID
-	SPOTIFY_CLIENT_SECRET

Estas credenciales se pueden obtener en el Portal de Desarrolladores de Spotify.

### Ejecución
Para ejecutar esta aplicación localmente, necesitas instalar las librerías mediante el siguiente comando:
```
pip install -r requirements.txt
```

Ejecuta la aplicación Streamlit:
```
streamlit run app.py
```

## Resultados Esperados

El proyecto permite al usuario obtener una experiencia interactiva con:
-	Visualización gráfica de las palabras más frecuentes en la letra.
-	Análisis emocional de las letras de las canciones para identificar si son positivas, negativas o neutrales.
-	Exploración de letras a partir de álbumes de estudio de artistas seleccionados.

## Conclusión

Este proyecto combina varias herramientas y APIs para proporcionar una experiencia interactiva que no solo permite explorar la música de los artistas, sino también realizar un análisis profundo de las letras de las canciones mediante técnicas de procesamiento de lenguaje natural. La interfaz intuitiva de Streamlit facilita la interacción con los datos, y los análisis proporcionan información valiosa sobre el contenido emocional de las canciones.


