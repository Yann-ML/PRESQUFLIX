import requests
import streamlit as st
from streamlit_authenticator import Authenticate
import pandas as pd
import plotly_express as px
import seaborn as sns
import matplotlib.pyplot as plt
# Import du module d'écriture
from st_keyup import st_keyup
# Importation du module
from streamlit_option_menu import option_menu
from fonction import *
# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('movie_stats.csv')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10


headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# définition de la fonction d'affichage du top 2 à 4 pour éviter de retaper le code
def fn_top_1(df, max_films =1):

    # initialisation de 6 colonnes
    cols = st.columns(2)

    # variable d'affichage max
    max_films = 1

    # boucle sur le range maxi de la variable d'affichage
    for i in range(max_films):
        # colonne pour info à afficher (titre, réal, année, durée, affiche cliquable)
        with cols[i * 2]:  # définition des colonnes impaires
            # iterrow pour boucler sur les lignes et récupérer les positions de chaque film sélectionné
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'poster_path' in row:
                    # définition de la position souhaitée
                    if pos == i:
                        # affichage des infos du film (titre, réal, année de sortie, durée) selon position définie
                        # double * pour mettre en gras entre les 3 guillemets (balises type html)
                        st.subheader(f'''**{row["title"]}**''')
                        st.markdown(f'''
                            **Réalisateur** : {row["director_name"]}  \n
                            **Année** : {row["startYear"]}  \n
                            **Durée** : {row["runtimeMinutes"]} min
                        ''')
                        # récup image dans le DF via poster_path
                        image_url = f'https://image.tmdb.org/t/p/w500/{row["poster_path"]}?language=fr'
                        # récup lien vers tmdb via l'id du film dans le DF
                        target_url = f'https://www.themoviedb.org/movie/{row["id"]}?language=fr'
                        # affichage de l'image en version cliquable
                        st.markdown(
                            f'<a href="{target_url}" target="_blank">'
                            f'<img src="{image_url}" width="300"></a>',
                            unsafe_allow_html=True
                        )
                        
                        url_video = f"https://api.themoviedb.org/3/movie/{row['id']}/videos"

                        response_video = requests.get(url_video, headers=headers)

                        video_data = response_video.json().get('results', [])

                        trailers = [
                            ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                            ]
                        if trailers:
                            trailer_key = trailers[0]['key']
                            youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                            st.write('Bande-annonce:')
                            st.video(youtube_url)
                            # break pour passer au prochain film de la boucle sur max_films
                            break

        # colonne à droite de la première pour les infos complémentaires du même film (acteurs + synopsis)
        with cols[i * 2 + 1]: # définition des colonnes paires
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'overview' in row:
                    if pos == i:
                        # affichage acteurs
                        st.write(f'**Acteurs** : {row["actor_name"]}')
                        # récupération url via API TMDB en fonction de l'id dans le DF
                        url = f"https://api.themoviedb.org/3/movie/{row['id']}?language=fr"
                        response = requests.get(url, headers=headers)
                        # récupération du synopsis si existant
                        synopsis = response.json().get('overview', 'Aucun synopsis disponible.')
                        # affichage synopsis
                        st.write(f"""
                            <div style="text-align: justify;">
                            {synopsis}
                            </div>
                        """, unsafe_allow_html=True)
                        # break pour passer au prochain film de la boucle sur max_films
                        break

# définition de la fonction d'affichage du top 2 à 4 pour éviter de retaper le code
def fn_top_films(df, max_films =3):

    # initialisation de 6 colonnes
    cols = st.columns(6)

    # variable d'affichage max
    max_films = 3

    # boucle sur le range maxi de la variable d'affichage
    for i in range(max_films):
        # colonne pour info à afficher (titre, réal, année, durée, affiche cliquable)
        with cols[i * 2]:  # définition des colonnes impaires
            # iterrow pour boucler sur les lignes et récupérer les positions de chaque film sélectionné
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'poster_path' in row:
                    # définition de la position souhaitée
                    if pos == i:
                        # affichage des infos du film (titre, réal, année de sortie, durée) selon position définie
                        # double * pour mettre en gras entre les 3 guillemets (balises type html)
                        st.subheader(f'''**{row["title"]}**''')
                        
                        # récup im
                        # récup image dans le DF via poster_path
                        image_url = f'https://image.tmdb.org/t/p/w500/{row["poster_path"]}?language=fr'
                        # récup lien vers tmdb via l'id du film dans le DF
                        target_url = f'https://www.themoviedb.org/movie/{row["id"]}?language=fr'
                        # affichage de l'image en version cliquable
                        st.markdown(
                            f'<a href="{target_url}" target="_blank">'
                            f'<img src="{image_url}" width="200"></a>',
                            unsafe_allow_html=True
                        )
                        
                        url_video = f"https://api.themoviedb.org/3/movie/{row['id']}/videos"

                        response_video = requests.get(url_video, headers=headers)

                        video_data = response_video.json().get('results', [])

                        trailers = [
                            ele for ele in video_data if ele['type'] == 'Trailer' and ele['site'] == 'YouTube'
                            ]
                        if trailers:
                            trailer_key = trailers[0]['key']
                            youtube_url = f"https://www.youtube.com/watch?v={trailer_key}"
                            st.write('Bande-annonce:')
                            st.video(youtube_url)
                            # break pour passer au prochain film de la boucle sur max_films
                            break

        # colonne à droite de la première pour les infos complémentaires du même film (acteurs + synopsis)
        with cols[i * 2 + 1]: # définition des colonnes paires
            for pos, (index, row) in enumerate(df.iterrows()):
                if 'overview' in row:
                    if pos == i:
                        # affichage acteurs
                        st.markdown(f'''
                            **Réalisateur** : {row["director_name"]}  \n
                            **Acteur(s)** : {row["actor_name"]} \n
                            **Actrice(s)** : {row["actress_name"]} \n
                            **Année** : {row["startYear"]}  \n
                            **Durée** : {row["runtimeMinutes"]} min \n
                            **Note** : {row["averageRating"]}
                        ''')
                        # st.write(f'\n **Acteurs** : {row["actor_name"]}')
                        # récupération url via API TMDB en fonction de l'id dans le DF
                        url = f"https://api.themoviedb.org/3/movie/{row['id']}?language=fr"
                        response = requests.get(url, headers=headers)
                        # récupération du synopsis si existant
                        synopsis = response.json().get('overview', 'Aucun synopsis disponible.')
                        # affichage synopsis
                        st.write(f"""
                                 **Synopsis**: \n
                            <div style="text-align: justify;">
                            {synopsis}
                            </div>
                        """, unsafe_allow_html=True)
                        # break pour passer au prochain film de la boucle sur max_films
                        break
