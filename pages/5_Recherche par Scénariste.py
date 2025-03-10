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

st.set_page_config(page_title='Scénaristes',
                   layout="wide")
headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10

# créer la liste des acteurs depuis le DF de base, en "explosant" chaque cellule, et ne gardant que les valeurs uniques, par ordre alpha
liste_scenariste = sorted((film_dataframe['writer_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

# ajout valeur par défaut à la liste pour affichage qui se trouvera toujours à la fin de la liste
liste_scenariste.append('Veuillez choisir un scénariste')

st.title('Recherche par scénariste')
st.write(f"{len(liste_scenariste)} scénaristes")

# cellule de sélection de l'acteur selon la liste définie précédemment
scen_choisi = st.selectbox("Choix du scénariste :", 
                            liste_scenariste, 
                            index=(len(liste_scenariste) - 1)) # pour récupérer la valeur au dernier indice de la liste

# affichage ligne de démarcation
st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

if scen_choisi != 'Veuillez choisir un scénariste':
    
    # afficher le nombre de films dans lesquels a joué l'acteur recherché
    st.subheader(f"{scen_choisi} a participé au scénario de {film_dataframe['writer_name'].str.contains(scen_choisi, na=False).sum()} films")
    
    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)
    
    # déclaration de 2 colonnes
    col1, col2 = st.columns(2)
    with col1:

        genres = film_dataframe["genres"].apply(lambda x: x.split(','))\
                                        .explode().value_counts().head(5).reset_index()

        # TOP 10 d'un scénariste choisi

        # 1er tri pour afficher les infos du DF en fonction du nom choisi par l'utilisateur, en filtrant sur le type 'movie', et en ne prenant que les 10 premiers
        scen_search = film_dataframe[(film_dataframe["writer_name"].str.contains(scen_choisi)) & \
                                (film_dataframe['titleType'] == 'movie')]\
                                .drop_duplicates(subset="tconst")\
                                .sort_values(by='averageRating', ascending=False)\
                                .head(10)

        # histo Top 10 films de l'acteur recherché
        graph_scen_search = px.bar(data_frame=scen_search.sort_values(by='averageRating').head(10),
                                x='averageRating',
                                y='title',
                                text_auto=True,
                                title=f'Top 10 films de {scen_choisi}',
                                labels={'averageRating': 'Note moyenne',
                                        'title': 'Film'})

        # titre en gras et centré
        graph_scen_search.update_layout(
            title={'text': f'<b>Top 5 des genres des films réalisé par {scen_choisi}</b>', 'x': 0.2}
            )
        
        st.plotly_chart(graph_scen_search)

    with col2:

        # camembert de répartition du Top 5 des genres pour l'acteur recherché
        graph_genre = px.pie(data_frame=scen_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                            values="count",
                            names= scen_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])
        # valeurs en gras
        graph_genre.update_traces(textinfo='percent+label',
                                texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                )

        # titre en gras et centré
        graph_genre.update_layout(
            title={'text': f'<b>Top 5 des genres des films réalisé par {scen_choisi}</b>', 'x': 0.5}
            )
        st.plotly_chart(graph_genre, theme=None)

    # afficher les affiches du top 3 en version cliquable vers TMDB
    st.subheader(f"Top Films de {scen_choisi}")
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

    # récup fonction pour top 2 à 4
    fn_top_films(scen_search, max_films=3)

    #--------------------------- AFFICHAGE TOUS FILMS ---------------------------

    # affichage DF avec tous les films de l'acteur/trice choisi
    with st.expander(f"Cliquer pour afficher tous les films écrits par {scen_choisi}"):
        st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                        [film_dataframe['writer_name']\
                        .str.contains(scen_choisi)]\
                        .sort_values(by='averageRating', ascending=False)\
                        .rename(columns={'title' : 'Titre',
                                        'averageRating' : 'Note moyenne',
                                        'startYear' : 'Année de Sortie',
                                        'genres' : 'Genre(s)',
                                        'actor_name' : 'Acteur(s)',
                                        'actress_name' : 'Actrice(s)',
                                        'writer_name' : 'Scénariste(s)'}),
                    hide_index=True)