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

from fonction import *

st.set_page_config(page_title='Acteurs/Actrices',
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
liste_actor = sorted((film_dataframe['actor_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())
liste_actrice = sorted((film_dataframe['actress_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

# créer une seule liste contenant les acteurs et actrices
liste_acteur = sorted(set(liste_actor + liste_actrice))

# ajout valeur par défaut pour affiche
liste_acteur.append('Veuillez choisir un(e) acteur(trice)')

st.title('Recherche par actrice/acteur')
st.write(f"{len(liste_acteur)} actrices/acteurs")

# cellule de sélection de l'acteur selon la liste définie précédemment
acteur_choisi = st.selectbox("Choix de l'acteur :",
                                liste_acteur,
                                index=(len(liste_acteur) - 1))

# affichage ligne de démarcation
st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

# afficher les éléments seulement si un acteur est sélectionné:
if acteur_choisi != 'Veuillez choisir un(e) acteur(trice)':

    # afficher le nombre de films dans lesquels a joué l'acteur recherché
    st.subheader(f"{acteur_choisi} a tourné dans {film_dataframe['actor_name'].str.contains(acteur_choisi, na=False).sum()} films") 

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # déclaration de 2 colonnes
    col1, col2 = st.columns(2)

    with col1:

        genres = film_dataframe["genres"].apply(lambda x: x.split(','))\
                                        .explode().value_counts().head(5).reset_index()

        # 1er tri pour afficher les infos du DF en fonction du nom choisi par l'utilisateur, en filtrant sur le type 'movie', et en ne prenant que les 10 premiers
        act_search = film_dataframe[(film_dataframe["actor_name"].str.contains(acteur_choisi)) & \
                                    (film_dataframe['titleType'] == 'movie')]\
                                    .drop_duplicates(subset="tconst")\
                                    .sort_values(by='averageRating', ascending=False)\
                                    .head(10)

        # histo Top 10 films de l'acteur recherché
        graph_search = px.bar(data_frame=act_search.sort_values(by='averageRating').head(10),
                                    x='averageRating',
                                    y='title',
                                    text='averageRating',
                                    title=f'Top 10 films de \n{acteur_choisi}',
                                    labels={'averageRating': 'Note moyenne',
                                            'title': ''})
        
        # mettre en gras les données et les positionner à l'extérieur du graph
        graph_search.update_traces(
                    texttemplate='<b>%{text}</b>',
                    textposition='outside'
                    )
        # centrer le titre du graph et mettre en ordre décroissant
        graph_search.update_layout(
                    yaxis=dict(categoryorder='total ascending'),
                    title={'x':0.5}
                    )
        # affichage graph et theme none pour bien distinguer du fond de streamlit
        st.plotly_chart(graph_search)

    with col2:

        # camembert de répartition du Top 5 des genres pour l'acteur recherché
        graph_genre = px.pie(data_frame=act_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                                values='count',
                            names= act_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])

        # valeurs en gras
        graph_genre.update_traces(textinfo='percent+label',
                                texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                )

        # titre en gras et centré
        graph_genre.update_layout(
            title={'text': f'<b>Top 5 des genres des films réalisé par {acteur_choisi}</b>', 'x': 0.2})

        st.plotly_chart(graph_genre)

    # afficher les affiches du top 3 en version cliquable vers TMDB
    st.subheader(f'Top Films de {acteur_choisi}')
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # récupération de la fonction d'affichage du top 2 à 4
    fn_top_films(act_search, max_films=3)

    #--------------------------- AFFICHAGE TOUS FILMS ---------------------------

    # affichage DF avec tous les films de l'acteur/trice choisi
    with st.expander(f"Cliquer pour afficher tous les films avec {acteur_choisi}"):
        st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]
                            [(film_dataframe['actor_name'].str.contains(acteur_choisi, na=False)) |
                            (film_dataframe['actress_name'].str.contains(acteur_choisi, na=False))]
                            .sort_values(by='averageRating', ascending=False)
                            .rename(columns={'title': 'Titre',
                                            'averageRating': 'Note moyenne',
                                            'startYear': 'Année de Sortie',
                                            'genres': 'Genre(s)',
                                            'actor_name': 'Acteur(s)',
                                            'actress_name': 'Actrice(s)',
                                            'writer_name': 'Scénariste(s)'}),
                    hide_index=True)
