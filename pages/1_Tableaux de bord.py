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

st.set_page_config(layout="wide")

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10
st.header('Tableaux de bords')

with st.expander("Acteurs/trices - Réalisateurs - Scénaristes"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        # tableau des acteurs les plus représentés
        st.subheader('Acteurs les plus présents')
        st.dataframe((film_dataframe['actor_name'][film_dataframe['actor_name'] != 'NC'].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(10).reset_index())\
                                            .rename(columns={'actor_name' : 'Acteurs', 'count': 'Nombre de films'}),
                                            hide_index=True)

    with col2:
        # tableau des acteurs les plus représentés
        st.subheader('Actrices les plus présentes')
        st.dataframe((film_dataframe['actress_name'][film_dataframe['actress_name'] != 'NC'].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(10).reset_index())\
                                            .rename(columns={'actress_name' : 'Actrices', 'count': 'Nombre de films'}),
                                            hide_index=True)

    with col3:
        # tableau des réalisateurs les plus représentés
        st.subheader('Réalisateurs les plus présents')
        st.dataframe((film_dataframe['director_name'][film_dataframe['director_name'] != 'NC'].apply(lambda x: x.split(','))\
                                        .explode().value_counts().head(10).reset_index())\
                                        .rename(columns={'director_name' : 'Réalisateur', 'count': 'Nombre de films'}),
                                        hide_index=True)
    with col4:
        # tableau des scénaristes les plus représentés
        st.subheader('Scénaristes les plus présents')
        st.dataframe((film_dataframe['writer_name'][film_dataframe['writer_name'] != 'NC'].apply(lambda x: x.split(','))\
                                            .explode().value_counts().head(10).reset_index())\
                                            .rename(columns={'writer_name' : 'Scénariste', 'count': 'Nombre de scénarios'}),
                                            hide_index=True)
        
    # En-tête de l'application
    st.header("Acteurs/actrices dans les films/Séries TV")
    col1, col2  = st.columns(2)
    # Listes pour les sélections
    with col1:
        st.write("Top 20 acteurs/actrices")
        list_actor = ["actor_name", "actress_name"]
        list_classer = ["Films", "Séries TV"]

    # Sélection utilisateur
        actor = st.selectbox("Rechercher un(e) acteur(trice)", list_actor)
        classer = st.selectbox("Classer selon nombre de films ou séries TV", list_classer)

        df_actor = pd.merge(
            left=film_dataframe.loc[film_dataframe['titleType'] == "movie", actor]
            .dropna()
            .apply(lambda x: x.split(","))
            .explode()
            .value_counts()
            .to_frame("Films"),
            right=film_dataframe.loc[film_dataframe['titleType'] == "tvSeries", actor]
            .dropna()
            .apply(lambda x: x.split(","))
            .explode()
            .value_counts()
            .to_frame("Séries TV"),
            left_index= True,
            right_index= True,
            how='inner'
            )

    # Créer les DataFrames pour les acteurs ou actrices
        if actor:
        # Trier et afficher les résultats
            if classer:
                df_actor = df_actor.iloc[1:,].sort_values(by=classer, ascending=False).head(20)
                st.table(df_actor)

        else:
            st.write("Veuillez sélectionner un critère pour afficher les données")
    with col2:
        st.write("Recherche par nom")
    #liste de nom d'actor ou d'actress
        list_actress = sorted(film_dataframe['actress_name'].dropna().apply(lambda x: x.split(",")).explode().unique())
        list_actor = sorted(film_dataframe['actor_name'].dropna().apply(lambda x: x.split(",")).explode().unique())

    #creation de selectionbox
        actress = st.checkbox("Rechercher une actrice")
        actor = st.checkbox("Rechercher un acteur")
        if actress:
            actress_name = st.selectbox("Sélectionner une actrice", list_actress,index= None)
            if actress_name:
                # nb_films = int(film_dataframe.loc[(film_dataframe['titleType'] == "movie") & ( film_dataframe['actress_name'].str.contains(actress_name))]['titleType'].value_counts().sum())
                # nb_series = int(film_dataframe.loc[(film_dataframe['titleType'] == "tvSeries") & ( film_dataframe['actress_name'].str.contains(actress_name))]['titleType'].value_counts().sum())
                st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "movie") & (film_dataframe["actor_name"].str.contains(actress_name))]["titleType"].value_counts().sum())} films')
                st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "tvSeries") & (film_dataframe["actor_name"].str.contains(actress_name))]["titleType"].value_counts().sum())} séries TV')
        
        elif actor:
            actor_name = st.selectbox("Rechercher un acteur ?", list_actor,index= None)
            if actor:
                # nb_films = int(film_dataframe.loc[(film_dataframe['titleType'] == "movie") & (film_dataframe['actor_name'].str.contains(actor_name))]['titleType'].value_counts().sum())
                # nb_series = int(film_dataframe.loc[(film_dataframe['titleType'] == "tvSeries") & (film_dataframe['actor_name'].str.contains(actor_name))]['titleType'].value_counts().sum())
                st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "movie") & (film_dataframe["actor_name"].str.contains(actor_name))]["titleType"].value_counts().sum())} films')
                st.write(f'Présent dans {int(film_dataframe.loc[(film_dataframe["titleType"] == "tvSeries") & (film_dataframe["actor_name"].str.contains(actor_name))]["titleType"].value_counts().sum())} séries TV')
                
        else:
            st.write("Veuillez sélectionner un critère pour afficher les données")


# ---------------------------------------- REPARTITION GENRES ------------------------------------

with st.expander("Genres"):
    
    df_films = film_dataframe[film_dataframe['titleType'] == "movie"]
    df_films.dropna(subset= ['revenue', 'popularity', 'id', 'budget'],inplace= True) 

    df_genres = pd.read_csv("https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/df_genres.zip")
    def fn_count_genre(var):
        var = str(var)
        var.count(",")
        return (var.count(",") + 1)
    
    df_films['nb_genres'] = df_films['genres'].apply(lambda x: fn_count_genre(x))

    # genre =df_films['genres'].loc[df_films['genres'] != "\\N"]\
    #                 .apply(lambda x: x.split(',')).explode()\
    #                     .value_counts().sort_values(ascending= False).head(10)

    # st.dataframe(df_films['genres'].value_counts())

    # st.dataframe(genre)
    
    #########
    st.header("Les Genres de films ")
    graph_top10 = px.bar(data_frame=df_films['genres'].loc[df_films['genres'] != "\\N"]\
                    .apply(lambda x: x.split(',')).explode()\
                        .value_counts().sort_values(ascending= False).head(10),
                x='count',
                text_auto=True,
                labels={"count" : "Nombre",
                        "genres" : "Genres"},
                title= f'Top 10 des genres' )
    st.plotly_chart(graph_top10)
    
    # --------------------------------------------------------------
    
    st.write("Sélectionnez le graphique souhaité:") 
    
    list_genre = sorted(df_genres['Genres'])
    
    col1, col2 = st.columns(2)
    with col1:
        TopNumber = st.checkbox("Répartition de films selon le nombre de genres")
    with col2:  
        Toprevenue = st.checkbox("Revenu moyen par nombre de genres")
    ##########
    
    col1, col2 = st.columns(2)
    with col1:
    
        if TopNumber:
            graph_pourcentage = px.pie(data_frame= df_films['nb_genres'].value_counts(normalize= True),
                                names=df_films['nb_genres'].value_counts(normalize= True).reset_index()['nb_genres'],
                                values= 'proportion',
                                labels={'1':'1 genre','2':'2 genres','3':'3 genres',
                                        'proportion':'Pourcentage de film'},
                                title= f'Répartition de films selon nombre de genres')
            st.plotly_chart(graph_pourcentage)

    with col2:

        if Toprevenue:
            tb_revenue_genres = {}
            for i in [1,2,3]:
                mean_revenue = round(df_films['revenue'].loc[(df_films['nb_genres']== i) & (df_films['revenue'] != 0)].mean(),3)
                tb_revenue_genres.update({ i : mean_revenue})
            graph_toprevenue = px.bar( x= tb_revenue_genres.keys(),y= tb_revenue_genres.values(),
                                    text_auto=True,
                                    labels= ({"x": "Nombre de genre par film",
                                                "y" : "Revenu moyen"}),
                                    title= f'Revenu moyen par nombre de genres')
            st.plotly_chart(graph_toprevenue)

        
    genre = st.selectbox("Sélectionner le genre",list_genre, index= None)
    
    ##############
    if genre:
        tb_genre = df_genres.loc[(df_genres['Genres'].str.contains(genre,na= False)) & (df_genres['Revenu moyen (millions)'] != 0)]
        st.write("Caractéristiques du genre sélectionné")
        st.dataframe(tb_genre,hide_index= True)
        data_genre = df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['revenue'] != 0)]
        st.header("Sélectionner une statistique")  
        col1, col2= st.columns(2)
        with col1:
            graph_number= st.checkbox("Total de films par décennie")
            graphique_duree = st.checkbox("Le durée de films par décennie") 
        with col2:
            graphique_revenue = st.checkbox("Revenu & Note")
            graph_buget = st.checkbox("Revenu & Budget")   
        
        if graph_number:
            graph_total = px.histogram(data_genre,
                                       x="decade",
                                       labels=({"decade" : "Décennies",
                                        "count" : "Nombre"}),
                                       text_auto=True)
            st.plotly_chart(graph_total)
                
        if graphique_duree:
                st.line_chart(data_genre, y='runtimeMinutes', x='decade', x_label= "Décennie", y_label= "Durée du film")   
        
        if graphique_revenue:
                st.bar_chart(data_genre, y='revenue', x='averageRating', x_label= "Note", y_label= "Revenu")
        
        if graph_buget:
                st.line_chart(data_genre, y='revenue', x='budget', x_label= "Budget", y_label= "Revenu")
        st.header("Les meilleurs films du genre sélectionné")
        
        col1, col2= st.columns(2)
        
        with col1: 
            list_trier = ['Note moyenne','Revenu']
            trier = st.selectbox("Classer par note ou revenu",list_trier, index= None)
        with col2:
            list_decennie = sorted(data_genre['decade'].unique())
            decennie = st.selectbox("Sélection de la décennie",list_decennie, index= None)
        
        df_stat = data_genre[['title','startYear', 'runtimeMinutes','genres', 'averageRating', 'numVotes', 'budget','revenue','popularity','actor_name', 'actress_name','director_name', 'writer_name','decade']]\
            .rename(columns={'title': 'Title','startYear': 'Année de sortie','runtimeMinutes': 'Durée (min)','genres': 'Genres','averageRating': 'Note moyenne','numVotes': 'Nombre de votes','budget': 'Budget (millions)',\
                'revenue' : 'Revenue (millions)', 'popularity': 'Popularité','actor_name': 'Acteurs','actress_name': 'Actrices','writer_name': 'Scénariste','director_name': 'Réalisateurs'})

        if decennie:
            df_stat = df_stat.loc[df_stat['decade'] == decennie] 
        if trier:
            df_stat = df_stat.sort_values(by=trier,ascending= False) 
        else:
            df_stat = df_stat.sort_values(by='Revenue (millions)', ascending= False).head(5)
        st.dataframe(data= df_stat,hide_index= True)
    ###################
        # st.header("Les meilleurs Acteurs/Actrices dans ce genre")
        tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        if decennie:
            tb_actress = df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['decade'] == decennie)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            tb_actor =  df_films.loc[(df_films['genres'].str.contains(genre)) & (df_films['decade'] == decennie)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        else:
            tb_actress = df_films.loc[df_films['genres'].str.contains(genre)]['actress_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
            tb_actor =  df_films.loc[df_films['genres'].str.contains(genre)]['actor_name'].dropna().apply(lambda x: x.split(",")).explode().value_counts().head(10).to_dict()
        
        st.subheader("Acteurs et actrices les plus présents dans la décennie sélectionnée")
        
        col1,col2 = st.columns(2)
        with col1:
            graph_actrices10 = px.bar(x=list(sorted(tb_actress.values())),
                                y=list(tb_actress.keys()),
                                text_auto=True,
                                labels=({"x" : "Nombre",
                                    "y" : "Nom d'actrice"}),
                                title= f'Top 10 actrices')
            st.plotly_chart(graph_actrices10)
        with col2:
            graph_acteur10 = px.bar(x=list(sorted(tb_actor.values())),
                                y=list(tb_actor.keys()),
                                text_auto=True,
                                labels=({"x" : "Nombre",
                                    "y" : "Nom d'acteur"}),
                                title= f'Top 10 acteurs')
            st.plotly_chart(graph_acteur10)

# ---------------------------------------- EVOLUTION DUREE FILMS DECENNIE ------------------------------------

# création d'un DF sur la durée
duree = film_dataframe[['tconst', 'runtimeMinutes', 'startYear', 'titleType']]\
        [(film_dataframe['runtimeMinutes'] != 0) & (film_dataframe['runtimeMinutes'] != '\\N') &\
        (film_dataframe['startYear'] != 0) & (film_dataframe['startYear'] != '\\N') &\
        (film_dataframe['titleType'] == 'movie')]\
        .drop_duplicates(subset='tconst')

# bascule en numérique de toutes les valeurs
duree['startYear'].apply(lambda x: int(x))
duree['runtimeMinutes'].apply(lambda x: int(x))
duree['startYear'] = duree['startYear'].apply(pd.to_numeric)
duree['runtimeMinutes'] = duree['runtimeMinutes'].apply(pd.to_numeric)

# création dico vide
dico_duree = {}
# boucle sur les années par dizaine
for annee in range(1900, 2023, 10):
    # print(year)
    dico_duree[annee]=round(duree[(duree['startYear']>=annee)&(duree['startYear']<=annee+10)]['runtimeMinutes'].mean(),2)

# création d'un DF particulier pour l'affichage
duree_moy = pd.DataFrame(list(dico_duree.items()), columns=["Décennie", "Durée_moyenne"]) 

with st.expander("Evolution de la durée des films"):
    # affichage de la stats
    evo_duree = px.line(data_frame=duree_moy,
                        x='Décennie',
                        y='Durée_moyenne',
                        title='Evolution de la durée moyenne des films',
                        labels={'Durée_moyenne' : 'Durée moyenne'}
                        )

    st.plotly_chart(evo_duree, theme=None)