import numpy as np
import pandas as pd
import streamlit as st

df = pd.read_csv('https://query.data.world/s/6scua2opjdjrwijmpfnogvkpu6aael')
words = df.groupby('word')
words.get_group('fucking').head()

url_RB = """https://youtu.be/R-LDKfhDD9I"""
url_PF = """https://youtu.be/Pxzeq4pYpXI"""

st.write(f"### Hello, what film are you interested in?")
film = 'RB'
if st.button('Reservoir dogs'):
    st.video(url_RB)
if st.button('Pulp fiction'):
    st.video(url_PF)



