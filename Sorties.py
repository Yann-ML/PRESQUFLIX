import requests
import streamlit as st

import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Importation du module
from streamlit_option_menu import option_menu

from fonction import *

# Données fixes pour le DataFrame
film_dataframe = pd.read_csv('https://raw.githubusercontent.com/Yann-ML/PRESQUFLIX/main/movie_stats.zip')
# ajout de la decennie au DF (oublié dans le DF de base...)
film_dataframe['decade'] = (film_dataframe['startYear'] // 10) * 10


from bs4 import BeautifulSoup
import requests
import pandas as pd
import re
from datetime import datetime, date, timedelta



st.set_page_config(page_title = "Presqu'Flix",
                   layout="wide")

st.sidebar.image('LOGO.webp')

headers = {
    "accept": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzliMjE5OTY2YjFiYTczNDliMTFiNjQxNWQ2ZGFjZiIsIm5iZiI6MTczNDU5NjIxNi45NTM5OTk4LCJzdWIiOiI2NzYzZDY3ODU4MWEzYzA1MDdhYjBjODIiLCJzY29wZXMiOlsiYXBpX3JlYWQiXSwidmVyc2lvbiI6MX0.ep8YcNVjt4GmmtNlO6wYBoBJxfTNwVjs5Ug0B0PuMKI"
}

# créer 3 colonne pour placer l'image à la colonne 2, de manière à la centrer
col1, col2, col3 = st.columns([1,2,1])
with col1:
      st.write('')
        
with col2:
    st.image('LOGO.webp', width=250)
    
with col3:
    st.write('')
    
st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)    

col1, col2, col3 = st.columns([1,1,1])

with col1:
      st.write('')
        
with col2:
    st.header('Sorties de la semaine')
    
with col3:
    st.write('')

st.markdown("<hr style='border: 1px solid blue;'>", unsafe_allow_html=True)    

link = 'https://www.allocine.fr/film/sorties-semaine/'
html = requests.get(link)
soup = BeautifulSoup(html.text, 'html.parser')

# st.divider()

# conversion de la page en soup
program = soup.find_all('div', {'class' : 'card entity-card entity-card-list cf'})

# boucle sur la soup pour trouver les films et séances
for film in program:

    titres = film.find('a', {'class' : 'meta-title-link'})
    titre_text = titres.text.strip()
    
    col1, col2, col3 = st.columns([1,1,3])

    # affiches
    affiches = film.find_all('img', class_="thumbnail-img")
    
    # print(affiches) # OK infos du films
    
    for affiche in affiches:
        img = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg)', 
          str(affiche))
        # print(titre_text, img, synopsi)
        st.columns(3)
    
    with col1:
        
        # récupérer id du film
        id = re.findall(r"(?<=cfilm=)\d+(?=\.html)", 
                        str(titres))
        video = 'https://www.allocine.fr/video/player_gen_cmedia=19549962&cfilm=' + id[0] +'.html'

        st.markdown(
        f'<a href="{video}" target="_blank">'
        f'<img src="{img[0]}" width="300"></a>',
        unsafe_allow_html=True
    )
    
    with col2:
        
        # récupérer noms des films
        titres = film.find('a', {'class' : 'meta-title-link'})
        titre_text = titres.text.strip()
        st.header(titre_text)
        

    with col3:
        
        synopsis = film.find('div', {'class' : 'synopsis' })
        synopsi = synopsis.text.strip()     
            
        st.write(f'**{synopsi}**')