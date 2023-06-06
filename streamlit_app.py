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
import plotly.graph_objects as go
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from plotly.subplots import make_subplots


def main():
    # Configuring web page
    st.set_page_config(layout="wide")

    # Importing .css style sheet
    with open("static/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Loading datasets
    df_pts = pd.read_csv("points-injection.csv", sep=";")
    df_mois = pd.read_csv("production-mensuelle-biomethane.csv", sep=";")
    df_horaire = pd.read_csv("prod-nat-gaz-horaire-prov.csv", sep=";")

    # Dashboard ---->
    st.title("Production de Biométhane en France")
    st.markdown("---")

    # KPIs
    st.subheader("0. Statistiques")
    col1, col2, col3 = st.columns(3)
    col1.metric("Nombre de sites", str(len(df_pts)))
    col2.metric("1er site", df_pts["Date de mise en service"].min())
    col3.metric(
        "Capacité totale (GWh/an)",
        str(df_pts["Capacite de production (GWh/an)"].sum().round(1)),
    )

    # Layout
    col1, col2 = st.columns([2,1])
    with col1:
        
        st.subheader("1. Nombre de sites mis en service")

        # Prepare data
        df_pts_annee = df_pts.groupby(by="Annee mise en service").count().reset_index()

        df_pts_annee_plot = df_pts_annee[
            df_pts_annee["Annee mise en service"] != 2023
        ].rename(columns={"Nom du site": "Nombre de sites"})

        # 1. Line Plot
        fig = px.line(
            df_pts_annee_plot,
            x="Annee mise en service",
            y="Nombre de sites",
            title="De 2011 à 2022",
        )

        # Show
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("2. Localisation des sites")

        # Prepare Data
        df_pts[["latitude", "longitude"]] = df_pts[
            df_pts["Annee mise en service"] == 2022
        ]["Coordonnees"].str.split(", ", expand=True)

        df_sample = df_pts[df_pts["Annee mise en service"] == 2022][
            ["latitude", "longitude"]
        ]
        df_sample[["longitude"]] = df_sample[["longitude"]].astype(float)
        df_sample[["latitude"]] = df_sample[["latitude"]].astype(float)

        # 2. Map Plot
        st.map(df_sample)

    #
    col1 = st.columns(1)

    st.subheader("4. Production nationale horaire")

    # Prepare Data
    df_horaire[["annee", "mois", "jour"]] = df_horaire["Journée gazière"].str.split(
        "-", expand=True
    )

    #
    heures_liste = [
        "0" + str(i) + ":00" if i < 10 else str(i) + ":00" for i in range(24)
    ]

    col1_bis, col2_bis, col3_bis, col4_bis = st.columns(4)

    with col1_bis:
        # streamlit component
        date_1 = st.date_input(
            "Sélectionner une date de début:", datetime.date(2022, 1, 1)
        )
        # streamlit component
        h_min = st.selectbox(
            "Sélectionner une heure de début:", (heures_liste), index=6
        )

    with col2_bis:
        # streamlit component
        date_2 = st.date_input(
            "Sélectionner une date de fin:", datetime.date(2022, 1, 21)
        )
        # streamlit component
        h_max = st.selectbox(
            "Sélectionner une heure de fin:", (heures_liste), index=12
        )

    # Prepare data
    month_1 = "0" + str(date_1.month) if date_1.month < 10 else str(date_1.month)
    month_2 = "0" + str(date_2.month) if date_2.month < 10 else str(date_2.month)

    day_1 = "0" + str(date_1.day) if date_1.day < 10 else str(date_1.day)
    day_2 = "0" + str(date_2.day) if date_2.day < 10 else str(date_2.day)

    df_horaire_week = df_horaire.loc[
        (df_horaire["annee"] >= str(date_1.year))
        & (df_horaire["annee"] <= str(date_2.year))
        & (df_horaire["mois"] >= month_1)
        & (df_horaire["mois"] <= month_2)
        & (df_horaire["jour"] >= day_1)
        & (df_horaire["jour"] <= day_2)
    ]

    df_horaire_week = (
        df_horaire_week.drop(
            columns=[
                "id",
                "Annee/Mois",
                #'Journée gazière',
                "Production Journalière (MWh PCS)",
                "Opérateur",
                "Nombre de sites d'injection raccordés au réseau de transport",
                "Statut de la donnée",
                "annee",
                "mois",
                "jour",
            ]
        )
        .set_index("Journée gazière")
        .loc[:, h_min:h_max]
    )

    # 4. Bar Plot
    fig = px.bar(
        df_horaire_week,
        labels={
            "value": "Production (MWh PCS)",
            "variable": "Heure",
        },
        title=("Production Horaire Nationale"),
    )

    # Show
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns([1,2])

    with col1:
        
        st.subheader("3. Sites par capacité de production")

        # streamlit component
        top_value = st.slider("Top", 0, 30, 10)

    #     # Prepare data
        df_pts_bar = (
            df_pts[["Nom du site", "Capacite de production (GWh/an)"]]
            .sort_values("Capacite de production (GWh/an)", ascending=False)
            .head(top_value)
            .sort_values("Capacite de production (GWh/an)", ascending=True)
        )

        df_pts_bar["Nom du site"] = [x[:15] for x in df_pts_bar["Nom du site"]]

        # 3. Bar Plot
        fig = px.bar(
            df_pts_bar,
            y="Nom du site",
            x="Capacite de production (GWh/an)",
            orientation="h",
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("5. Capacite de production par région (%)")

        col1_ter, col2_ter, col3_ter, col4_ter = st.columns(4)

        with col1_ter:
            # streamlit component
            annee = st.selectbox(
                "Sélectionner une année:",
                (df_pts["Annee mise en service"].sort_values().unique().tolist()),
                index=10,
                key=1,
            )

        # Pepare Data
        df_pts_plot = df_pts[df_pts["Annee mise en service"] == annee][
            ["Region", "Capacite de production (GWh/an)"]
        ]

        # 5. Pie Plot
        fig = make_subplots(rows=1, cols=1, specs=[[{"type": "domain"}]])

        fig.add_trace(
            go.Pie(
                labels=df_pts_plot["Region"].to_list(),
                values=df_pts_plot["Capacite de production (GWh/an)"],
                name="GHG Emissions",
            ),
            1,
            1,
        )

        # Use `hole` to create a donut-like pie chart
        fig.update_traces(
            hole=0.7,
            hoverinfo="label+percent+name",
            pull=[0, 0, 0, 0.2, 0, 0, 0, 0, 0, 0, 0, 0],
            textposition="outside",
        )

        fig.update_layout(
            title_text="Capacite de production par région (%) en " + str(annee)
        )

        st.plotly_chart(fig, use_container_width=True)


main()
