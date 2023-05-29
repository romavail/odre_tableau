import os
import math
import warnings
import folium
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly as plty
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
from folium.plugins import HeatMap
from streamlit_folium import st_folium



def main():

    st.title('Production de Biométhane - France')

    # LOAD

    df_pts = pd.read_csv("/datasets/points-injection.csv", sep=';')
    df_mois = pd.read_csv("/datasets/production-mensuelle-biomethane.csv", sep=';')
    df_horaire = pd.read_csv("/datasets/prod-nat-gaz-horaire-prov.csv", sep=';')

    # Section title
    st.subheader("Dataframe Production Horaire")

    #
    st.dataframe(df_horaire.head(5))

    # VISUALIZE 

    # 1. Line Plot

    # Section title
    st.subheader("Nombre De Sites Mis En Service Par An")

    # Pepare Data

    # Comptage des points d'injection
    df_pts_annee = (df_pts.groupby(by='Annee mise en service')
                            .count()
                            .reset_index())
    
    df_pts_annee_plot = df_pts_annee[df_pts_annee['Annee mise en service'] != 2023].rename(columns={"Nom du site": "Nombre de sites"})
    
    # Plot
    fig = px.line(df_pts_annee_plot, 
                  x="Annee mise en service", 
                  y="Nombre de sites", 
                  title='')
    
    # Show
    st.plotly_chart(fig, use_container_width=True)


    # 2. Pie Plot

    # Section title
    st.subheader("Part De La Capacite De Production Par Région (%)")

    #
    annee = st.selectbox('année:',
                        (df_pts['Annee mise en service'].sort_values().unique().tolist()),
                        index=7
                        )
    
    # Pepare Data
    df_pts_plot = df_pts[df_pts['Annee mise en service'] == annee][['Region',
                                                                   'Capacite de production (GWh/an)']]
    
    # Plot
    fig = px.pie(df_pts_plot, 
                 values='Capacite de production (GWh/an)', 
                 names='Region')
    
    fig.update_traces(textposition='inside',
                      hole=.6, 
                      hoverinfo="label+percent+name")

    fig.update_layout(uniformtext_minsize=12, 
                      uniformtext_mode='hide', 
                      title_text="")
    
    # Show
    st.plotly_chart(fig, use_container_width=True)
    

    # 3. Bar Plot

    # Section title
    st.subheader("Production Nationale Horaire ")

    # Prepare Data

    # Creation des colonnes 'jour', 'mois', 'annee' à partir de 
    # 'journee gazière' de la production Horaire
    df_horaire[['annee',
                'mois',
                'jour']] = df_horaire['Journée gazière'].str.split('-', expand=True)
    
    col1, col2, col3 = st.columns(3)

    with col1:
        annee = st.selectbox('année:',
                            (df_horaire['annee'].sort_values().unique().tolist())
                            )
    
        heures_liste = [
                        '00:00',
                        '01:00',
                        '02:00',
                        '03:00',
                        '04:00',
                        '05:00',
                        '06:00',
                        '07:00',
                        '08:00',
                        '09:00',
                        '10:00',
                        '11:00',
                        '12:00',
                        '13:00',
                        '14:00',
                        '15:00',
                        '16:00',
                        '17:00',
                        '18:00',
                        '19:00',
                        '20:00',
                        '21:00',
                        '22:00',
                        '23:00'
                        ]

    

    with col2:
        h_min = st.selectbox('heure min:',
                         (heures_liste),
                         index=0)

    with col3:
        h_max = st.selectbox('heure max:',
                         (heures_liste),
                          index=6)

    # Prepare data
    df_horaire_week = (df_horaire.loc[(df_horaire['annee'] >= str(annee)) &
                                      (df_horaire['annee'] <= str(annee)) 
                                     ] 
                                 .sort_values('jour')
                                 .drop(columns=['id', 
                                                'Annee/Mois',
                                                #'Journée gazière',
                                                'Production Journalière (MWh PCS)', 
                                                'Opérateur',
                                                "Nombre de sites d'injection raccordés au réseau de transport",
                                                'Statut de la donnée', 
                                                'annee', 
                                                'mois', 
                                                'jour'
                                               ]
                                      )
                                 .set_index('Journée gazière')
                                 .loc[:, h_min:h_max]
                        )
    #  Plot     
    fig = px.bar(df_horaire_week,
                    labels={
                        "value": "Production (MWh PCS)",
                        "variable": "Heure",
                    },
                    #orientation='h',
                
                    title=('Production Horaire Nationale en' + ' ' + str(annee))
                )

    # Show
    st.plotly_chart(fig, use_container_width=True)
    

    # 4. Folium Plot
    
    # Section title
    st.subheader("Localisation Des Sites De Production")
    st.subheader("")

    # Prepare Data 

    df_pts[['longitude', 'latitude']] = df_pts[df_pts['Annee mise en service'] == 2022]['Coordonnees'].str.split(', ', expand=True)

    df_sample = df_pts[df_pts['Annee mise en service'] == 2022][['longitude',
                                                                 'latitude']]
    
    # Plot 
    m = folium.Map(location=[46.7111,  1.7191],
                 zoom_start=6.2,
                 tiles="CartoDB Positron"
                 )

    # Heatmap
    HeatMap(df_sample,
             radius=14,
             min_opacity=0.7,
         ).add_to(m)

    # Add the Circles 
    df_sample.apply(lambda x:folium.Circle(location=[x['longitude'],
                                                     x['latitude']],
                                         radius=100,
                                         fill=False,
                                        color='black',
                                        ).add_to(m),
                     axis=1
                    )

    # Show
    st_folium(m, width=725)



main()