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

st.set_page_config(page_title='Réalisateurs',
                   layout="wide")
headers = {
"accept": "application/json",
"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10

# création liste réalisateurs
liste_realisateur = sorted((film_dataframe['director_name'].dropna().astype(str)).apply(lambda x: x.split(',')).explode().unique())

# ajout valeur par défaut à la liste pour affichage qui se trouvera toujours à la fin de la liste
liste_realisateur.append('Veuillez choisir un réalisateur')

# affichage titre section
st.title('Recherche par réalisateur')
st.write(f"{len(liste_realisateur)} réalisateurs")

# création select_box de choix du real en variable pour l'intégrer aux graphs et stats
realisateur_choisi = st.selectbox("Choix du réalisateur :", 
                                    liste_realisateur,
                                    index=(len(liste_realisateur) - 1)) # pour récupérer la valeur au dernier indice de la liste

real_search = film_dataframe[(film_dataframe["director_name"].str.contains(realisateur_choisi)) & \
                            (film_dataframe['titleType'] == 'movie')]\
                            .drop_duplicates(subset="tconst")\
                            .sort_values(by='averageRating', ascending=False)\
                            .head(10)

# affichage ligne de démarcation
st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

if realisateur_choisi != 'Veuillez choisir un réalisateur':

    # afficher le nombre de films réalisé
    st.subheader(f"{realisateur_choisi} a réalisé {film_dataframe['director_name'].str.contains(realisateur_choisi, na=False).sum()} films")

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:

        # Top 10 films du réalisateur
        graph_search = px.bar(data_frame=real_search.sort_values(by='averageRating').head(10),
                                    x='averageRating',
                                    y='title',
                                    text_auto=True,
                                    title=f'Top 10 films de \n{realisateur_choisi}',
                                    labels={'averageRating': 'Note moyenne',
                                            'title': 'Film'})

        # Mettre le titre en gras et centrer
        graph_search.update_layout(title={'text': f'<b>Top 10 films de \n{realisateur_choisi}</b>', 'x': 0.5})

        st.plotly_chart(graph_search)

    with col2:

        # camembert de répartition du Top 5 des genres pour l'acteur recherché
        graph_genre = px.pie(data_frame=real_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5),
                            values="count",
                            names= real_search["genres"].apply(lambda x: x.split(',')).explode().value_counts().head(5).reset_index()["genres"])

        # valeurs en gras
        graph_genre.update_traces(textinfo='percent+label',
                                texttemplate='<b>%{label}</b>: <b>%{percent}</b>'
                                )

        # titre en gras et centré
        graph_genre.update_layout(
            title={'text': f'<b>Top 5 des genres des films réalisé par {realisateur_choisi}</b>', 'x': 0.2}
            )

        st.plotly_chart(graph_genre)

    # afficher les affiches du top 3 en version cliquable vers TMDB
    st.subheader(f"Top Films de {realisateur_choisi}")
    st.markdown("<hr style='border: 1px solid black;'>", unsafe_allow_html=True)

    # ------------------------------------ TOP 2 à 4 FILMS REALISATEUR -----------------------------------

    # récup fonction affichage du top 2 à 4
    fn_top_films(real_search, max_films=3)

    # ------------------------------------ AFFICHAGE DF FILMS REALISATEUR -----------------------------------

    # récup fonction affichage du top 2 à 4
    with st.expander(f"Cliquer pour afficher tous les films de {realisateur_choisi}"):
        st.dataframe(data=film_dataframe[['title', 'averageRating', 'startYear', 'genres', 'actor_name', 'actress_name', 'writer_name']]\
                        [film_dataframe['director_name']\
                        .str.contains(realisateur_choisi)]\
                        .sort_values(by='averageRating', ascending=False)\
                        .rename(columns={'title' : 'Titre',
                                        'averageRating' : 'Note moyenne',
                                        'startYear' : 'Année de Sortie',
                                        'genres' : 'Genre(s)',
                                        'actor_name' : 'Acteur(s)',
                                        'actress_name' : 'Actrice(s)',
                                        'writer_name' : 'Scénariste(s)'}),
                    hide_index=True)
