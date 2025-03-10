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
from sklearn.feature_extraction.text import CountVectorizer
import random

st.set_page_config(page_title='Recommandations',
                   layout="wide")

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10
# -------------------------------- MACHINE LEARNING - RECOMMANDATIONS --------------------------------

# Création du DataFrame

df = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_reco.zip')

st.title('Bienvenue sur la page de recommandation automatique de film')

# st.dataframe(df)

# création liste films pour pouvoir ajouter le choix par défaut "Veuillez choisir un film"
liste_film = sorted((df['title'].dropna().astype(str)).unique())
# ajout du choix par défaut dans la liste
liste_film.append('Veuillez choisir un film')

text_search = st.selectbox(f'Choix du film : ',
                        liste_film,
                        index=(len(liste_film)-1)
                        )
if text_search != 'Veuillez choisir un film' :
    
    # Filter the dataframe using masks
    m1 = df["title"].str.contains(text_search, na=False)
    df_search = df[m1]

    # -------------------------- INTEGRATION DU ML VECTORIZER + NEARET NEIGHBORS ------------------------

    # Intégration du modèle de machine learning
    from sklearn.neighbors import NearestNeighbors
    vectorizer = CountVectorizer()

    # entrainement et transformation des données texte pour que le ML puisse les traiter
    X = vectorizer.fit_transform(df['combined_features'])

    # déclaration du modèle de NearestNeighbors
    modelNN = NearestNeighbors(n_neighbors=6,
                            metric='cosine'          
                            )

    # entrainement du modèle sur la colonne de features X
    modelNN.fit(X)

    # boucle

    features_film = X[df[df['title'].str.contains(text_search)].index[0]]

    # Gérez le cas où il y a moins de 2 correspondances
    # faire tourner le modèle ML de kneighbors par rapport aux features du film recherché
    distances, indices = modelNN.kneighbors(features_film, n_neighbors=30)

    # créer le DF qui contiendra les films recommandés en focntion des indices du modèle NN
    films_reco = df.iloc[indices[0]]

    # affichage du film et des éléments souhaités
    print(f"Films recommandés pour {text_search} :")

    print(films_reco.iloc[1:4]['title'])
    print(films_reco.iloc[1:4]['poster_path'])

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # ------------------------------------ RESULTATS DU ML --------------------------------

    # -------------------------------- AFFICHAGE DU FILM RECHERCHE -------------------------

    if text_search is not None:

        id_search = df_search.loc[df['title'] == text_search].iloc[0, 16]

        search_col1, search_col2, search_col3 = st.columns([1,2,2])

        with search_col1:

            df_search.reset_index()
            
            # récup image dans le DF via poster_path
            image_url = f'https://image.tmdb.org/t/p/w500/{df_search.iloc[0,20]}'
            # récup lien vers tmdb via l'id du film dans le DF
            target_url = f'https://www.themoviedb.org/movie/{df_search.iloc[0,16]}'
            # affichage de l'image en version cliquable
            st.markdown(
                f'<a href="{target_url}" target="_blank">'
                f'<img src="{image_url}" width="330"></a>',
                unsafe_allow_html=True
            )
            
        with search_col2:
            st.subheader('Informations sur le film')

            st.write(f'**Réalisateur** : {df_search.iloc[0,29]}')
            st.write(f'**Acteur(s)** : {df_search.iloc[0,27]}')
            st.write(f'**Actrice(s)** : {df_search.iloc[0,28]}')
            st.write(f'**Durée** : {df_search.iloc[0,5]} minutes')
            st.write(f'**Note** : {df_search.iloc[0,7]}/10')

            id_search = df_search.loc[df['title'] == text_search].iloc[0, 16] # Ce code me donne l'id du film cherché par l'user

            url = f"https://api.themoviedb.org/3/movie/{id_search}?language=fr"
            
            st.subheader('Résumé du film')
            response = requests.get(url, headers=headers)

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.write(texte, unsafe_allow_html=True)

        with search_col3:
            url_video = f"https://api.themoviedb.org/3/movie/{id_search}/videos"

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

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # ---------------------------- AFFICHAGE DES 3 FILMS RECOMMANDES LES PLUS PROCHES -------------------------

    # 3 colonnes pour centrer le titre en colonne 2
    col1, col2, col3 = st.columns(3)

    with col2:
        st.subheader('Films recommandés')

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    reco_col1, reco_col2, reco_col3, reco_col4, reco_col5, reco_col6 = st.columns(6)

    with reco_col1:

        st.subheader(f"**{films_reco.iloc[1,10]}**")
        
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[1,20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[1,16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )
        
        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[1,16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[1,10], 'id'].iloc[0])


    with reco_col2:

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        response = requests.get(url, headers=headers)

        st.write(f'**Réalisateur :** {films_reco.iloc[1,29]}')
        st.write(f'**Acteur(s):** {films_reco.iloc[1,27]}')
        st.write(f'**Actrice(s):** {films_reco.iloc[1,28]}')
        st.write(f'**Durée:** {films_reco.iloc[1,5]} minutes')
        st.write(f'**Note:** {films_reco.iloc[1,7]}/10')

        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    with reco_col3:

        st.subheader(f"**{films_reco.iloc[2,10]}**")
        
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[2,20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[2,16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )
        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[2,16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[2,10], 'id'].iloc[0])

    with reco_col4:

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        response = requests.get(url, headers=headers)

        st.write(f'**Réalisateur :** {films_reco.iloc[2,29]}')
        st.write(f'**Acteur(s) :** {films_reco.iloc[2,27]}')
        st.write(f'**Actrice(s) :** {films_reco.iloc[2,28]}')
        st.write(f'**Durée :** {films_reco.iloc[2,5]} minutes')
        st.write(f'**Note :** {films_reco.iloc[2,7]}/10')
        
        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    with reco_col5:

        st.subheader(f"**{films_reco.iloc[3,10]}**") 
        
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[3,20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[3,16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )
        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[3,16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[3,10], 'id'].iloc[0])

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

    with reco_col6:

        response = requests.get(url, headers=headers)

        st.write(f'**Réalisateur :** {films_reco.iloc[3,29]}')
        st.write(f'**Acteur(s) :** {films_reco.iloc[3,27]}')
        st.write(f'**Actrice(s) :** {films_reco.iloc[3,28]}')
        st.write(f'**Durée :** {films_reco.iloc[3,5]} minutes')
        st.write(f'**Note :** {films_reco.iloc[3,7]}/10')
        
        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # -------------------------------------- AFFICHAGE 3 FILMS "VOUS POURRIEZ AIMER" ---------------------

    # 3 colonnes pour centrer le titre en colonne 2
    col1, col2, col3 = st.columns(3)

    with col2:
        st.header('Vous pourriez aussi aimer')

    # affichage ligne de démarcation
    st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)

    # création liste pour ajouter les index de films complémentaires
    liste = []
    
    # tant que la liste n'a pas chiffres/index, continue
    while len(liste) < 3:
        num = random.randint(4, 29)
        if num not in liste:
            liste.append(num)
    
    # vérif longueur liste suite à problème d'index hors list"
    # st.write(len(liste))
    
    reco_col1, reco_col2, reco_col3, reco_col4, reco_col5, reco_col6 = st.columns(6)

    with reco_col1:

        st.subheader(f'{films_reco.iloc[liste[0],10]}')
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[0],20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[0],16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )
        
        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[0],16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[liste[0],10], 'id'].iloc[0])

    with reco_col2:

        st.write(f'**Réalisateur :** {films_reco.iloc[liste[0],29]}')
        st.write(f'**Acteur(s) :** {films_reco.iloc[liste[0],27]}')
        st.write(f'**Actrice(s) :** {films_reco.iloc[liste[0],28]}')
        st.write(f'**Durée :** {films_reco.iloc[liste[0],5]} minutes')
        st.write(f'**Note :** {films_reco.iloc[liste[0],7]}/10')

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        response = requests.get(url, headers=headers)

        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    with reco_col3:
        
        st.subheader(f'{films_reco.iloc[liste[1],10]}')   
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[1],20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[1],16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )

        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[1],16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[liste[1],10], 'id'].iloc[0])

    with reco_col4:

        st.write(f'**Réalisateur :** {films_reco.iloc[liste[1],29]}')
        st.write(f'**Acteur(s) :** {films_reco.iloc[liste[1],27]}')
        st.write(f'**Actrice(s) :** {films_reco.iloc[liste[1],28]}')
        st.write(f'**Durée :** {films_reco.iloc[liste[1],5]} minutes')
        st.write(f'**Note :** {films_reco.iloc[liste[1],7]}/10')

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"
        
        response = requests.get(url, headers=headers)

        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    with reco_col5:

        st.subheader(f'{films_reco.iloc[liste[2],10]}')
        # récup image dans le DF via poster_path
        image_url = f'https://image.tmdb.org/t/p/w500/{films_reco.iloc[liste[2],20]}'
        # récup lien vers tmdb via l'id du film dans le DF
        target_url = f'https://www.themoviedb.org/movie/{films_reco.iloc[liste[2],16]}'
        # affichage de l'image en version cliquable
        st.markdown(
            f'<a href="{target_url}" target="_blank">'
            f'<img src="{image_url}" width="280"></a>',
            unsafe_allow_html=True
        )
        
        url_video = f"https://api.themoviedb.org/3/movie/{films_reco.iloc[liste[2],16]}/videos"

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

        id_test = int(df.loc[df['title'] == films_reco.iloc[liste[2],10], 'id'].iloc[0])

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

    with reco_col6:

        st.write(f'**Réalisateur :** {films_reco.iloc[liste[2],29]}')
        st.write(f'**Acteur(s) :** {films_reco.iloc[liste[2],27]}')
        st.write(f'**Actrice(s) :** {films_reco.iloc[liste[2],28]}')
        st.write(f'**Durée :** {films_reco.iloc[liste[2],5]} minutes')
        st.write(f'**Note :** {films_reco.iloc[liste[2],7]}/10')
        
        response = requests.get(url, headers=headers)

        # Texte justifié avec HTML et CSS
        texte = f"""
        <div style="text-align: justify;">
            {response.json().get('overview', 'Aucun résumé disponible.')}
        </div>
        """
        # Afficher le texte avec justification
        st.write(texte, unsafe_allow_html=True)

    # ------------------------- AFFICHER LA COLLECTION SI LE FILM FAIT PARTIE D'UNE COLLECTION -------------------

    id_test = int(df.loc[df['title'] == text_search, 'id'].iloc[0])

    url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

    response = requests.get(url, headers=headers)

    data = response.json()

    # Cette ligne permet de traiter l'erreur dans le cas où le film n'appartient pas à une collection
    if data.get("belongs_to_collection") is not None:

        id_collection = response.json()['belongs_to_collection']['id']

        url = f"https://api.themoviedb.org/3/movie/{id_test}?language=fr"

        response = requests.get(url, headers=headers)

        id_collection = response.json()['belongs_to_collection']['id']

        # Nouvel URL pour la 2nde requête
        url_coll = f"https://api.themoviedb.org/3/collection/{id_collection}?language=fr"

        response_coll = requests.get(url_coll, headers=headers)

        st.divider()

        st.title('Autres films de la même collection')

        print(len(response_coll.json()['parts']))
        list_film_coll = []
        for film in range(len(response_coll.json()['parts'])):

            list_film_coll.append(response_coll.json()['parts'][film]['title'])


        resultats_film_col = [film for film in list_film_coll if film in df["title"].to_list()]

        choix_film_coll = st.selectbox('Liste des films de la même collection que le film recherché initialement : ', resultats_film_col)

        # Refaire une requête à l'API qui se base sur "choix_film_col"

        df_choix_coll = df.loc[df['title'] == choix_film_coll]

        film_coll1, film_coll2 = st.columns(2)

        with film_coll1:

            st.image(f'https://image.tmdb.org/t/p/w500{df_choix_coll.iloc[0,20]}', width = 300)

            id_reco = int((df_choix_coll.iloc[0,16]))

        with film_coll2:

            url = f"https://api.themoviedb.org/3/movie/{id_reco}?language=fr"

            response = requests.get(url, headers=headers)
            st.subheader('Résumé du film')

            # Texte justifié avec HTML et CSS
            texte = f"""
            <div style="text-align: justify;">
                {response.json().get('overview', 'Aucun résumé disponible.')}
            </div>
            """
            # Afficher le texte avec justification
            st.markdown(texte, unsafe_allow_html=True)