import requests
import streamlit as st

import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Importation du module
from streamlit_option_menu import option_menu
from sklearn.feature_extraction.text import CountVectorizer
import random

from fonction import fn_top_1, fn_top_films

st.set_page_config(page_title='Genres',
                   layout="wide")

headers = {
"accept": "application/json",
"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10

#  --------------------------------------------- SELECTION PAR GENRE --------------------------------------------

# affichage du titre de la section
st.title('Recherche par genre')

# création liste genres
liste_genre = sorted(set(film_dataframe['genres'].apply(lambda x: x.split(',')).explode().to_list()))
liste_genre.append('Veuillez choisir un genre')

# création liste nationalité des films
liste_nation = sorted(set(film_dataframe['production_countries'].dropna().apply(lambda x: x.split(',')).explode().to_list()))

nationalite = {
    "Veuillez choisir un pays de production": "",
    "États-Unis": "US",
    "France": "FR",
    "Autres": "Autres"
}

# sélection de la nationalité
natio_choisie = st.selectbox('Choix de la nationalité', list(nationalite.keys()))

# affichage des selectbox
col1, col2 = st.columns(2)

with col1:
    genre_choisi = st.selectbox('Choix du genre :', liste_genre, index=(len(liste_genre) - 1))

with col2:
    decennie_choisie = st.selectbox(
        "Choix de la décennie :",
        options=sorted(film_dataframe['decade'][film_dataframe['decade'] != 0].dropna().unique()),
        index=12
    )

# condition pour gérer le filtre 'Autres'
if genre_choisi != 'Veuillez choisir un genre' and natio_choisie != 'Veuillez choisir un pays de production':
    # si sélection nation = autre, on crée un DF qui prend les éléments inverses (~) de FR et US
    if natio_choisie == "Autres":
        # DF selon décennie, natio et genre choisi
        genre_search_decennie = film_dataframe[
            (film_dataframe["genres"].str.contains(genre_choisi)) & 
            (~film_dataframe['production_countries'].str.contains('FR|US', na=False)) &
            (film_dataframe['titleType'] == 'movie') & 
            (film_dataframe['numVotes'] > 5000) &
            (film_dataframe['decade'] == decennie_choisie)]\
            .drop_duplicates(subset="tconst")\
            .sort_values(by='averageRating', ascending=False)\
            .head(10)

        # DF pour affichage les films "hors decennie"
        genre_search = film_dataframe[
            (film_dataframe["genres"].str.contains(genre_choisi)) & 
            (~film_dataframe['production_countries'].str.contains('FR|US', na=False)) &
            (film_dataframe['titleType'] == 'movie') & 
            (film_dataframe['numVotes'] > 5000)]\
            .drop_duplicates(subset="tconst")\
            .sort_values(by='averageRating', ascending=False)\
            .head(10)
    # si sélection nation != autre, on crée un DF qui prend la valeur sélectionnée dans liste_natio
    else:
        # DF selon décennie, natio et genre choisi
        genre_search_decennie = film_dataframe[
            (film_dataframe["genres"].str.contains(genre_choisi)) & 
            (film_dataframe['production_countries'].str.contains(nationalite[natio_choisie], na=False)) &
            (film_dataframe['titleType'] == 'movie') & 
            (film_dataframe['numVotes'] > 5000) &
            (film_dataframe['decade'] == decennie_choisie)]\
            .drop_duplicates(subset="tconst")\
            .sort_values(by='averageRating', ascending=False)\
            .head(10)

        # DF pour affichage les films "hors decennie"
        genre_search = film_dataframe[
            (film_dataframe["genres"].str.contains(genre_choisi)) & 
            (film_dataframe['production_countries'].str.contains(nationalite[natio_choisie], na=False)) &
            (film_dataframe['titleType'] == 'movie') & \
            (film_dataframe['numVotes'] > 5000)]\
            .drop_duplicates(subset="tconst")\
            .sort_values(by='averageRating', ascending=False)\
            .head(10)
        
    st.header(f"Top 10 des films de {genre_choisi} de la décennie {decennie_choisie}")
    genre_top10 = px.bar(
        data_frame=genre_search_decennie.sort_values(by='averageRating', ascending=False).head(10),
        x='averageRating',
        y='title',
        text='averageRating',
        title=f'Top 10 des films du genre {genre_choisi}',
        labels={'averageRating': 'Note moyenne', 'title': 'Titre'}
    )
    genre_top10.update_traces(texttemplate='<b>%{text}</b>', textposition='outside')
    genre_top10.update_layout(yaxis=dict(categoryorder='total ascending'), title={'x': 0.5})
    st.plotly_chart(genre_top10)

    # ------------------------------- TOP 2 à 4 GENRE DE LA DECENNIE SELECTIONNEE ---------------------------

    # affichage titre section
    st.subheader(f'Top du genre {genre_choisi} et de la nationalité choisie des années {decennie_choisie}'
                ,divider='blue')

    # récup fonction affichage top 2 à 4
    fn_top_films(genre_search_decennie, max_films=3)

    # ----------------------------------- TOP 3 TOUTE ANNEES CONFONDUES ------------------------------------------

    # affichage titre section
    st.subheader(f"Top du genre {genre_choisi} et de la nationalité choisie"
                , divider='blue')

    # récup fonction affichage top 2 à 4 all time
    fn_top_films(genre_search, max_films=3)

    #--------------------------- AFFICHAGE TOUS FILMS ---------------------------
    
    # affichage DF avec tous les films du genre choisi
    with st.expander(f"Cliquer pour afficher tous les films appartenant au genre {genre_choisi}"):
        st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                        [film_dataframe['genres']\
                        .str.contains(genre_choisi)]\
                        .sort_values(by='averageRating', ascending=False)\
                        .rename(columns={'title' : 'Titre',
                                        'averageRating' : 'Note moyenne',
                                        'startYear' : 'Année de Sortie',
                                        'genres' : 'Genre(s)',
                                        'actor_name' : 'Acteur(s)',
                                        'actress_name' : 'Actrice(s)',
                                        'writer_name' : 'Scénariste(s)'}),
                    hide_index=True)
