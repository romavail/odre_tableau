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

    # Loading datasets
    df_pts = pd.read_csv("points-injection.csv", sep=";")
    df_mois = pd.read_csv("production-mensuelle-biomethane.csv", sep=";")
    df_horaire = pd.read_csv("prod-nat-gaz-horaire-prov.csv", sep=";")

   
    st.dataframe(df_pts)
    
       
main()
