import numpy as np
import matplotlib.pyplot as plt #1
import pandas as pd
import streamlit as st
import folium as fol
from bokeh.layouts import column, row
from bokeh.models import Slider
from bokeh.models.sources import ColumnDataSource
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.layouts import column, row
from streamlit_bokeh_events import streamlit_bokeh_events

#wines by countries, their ratings, price
# rating by their price
# price by their variety
# advicing vine by price
@st.cache
def get_data(url):
    df = pd.read_csv(url)
    return df

df = get_data('https://raw.githubusercontent.com/zhekaforest/HA/main/wines.csv')
new_df = df[df['price']<500]
new_df = new_df[new_df['price']>100]

def points_by_price(df, price):
    df = df[df['price']<=price+500]
    df = df[df['price']>=price]
    x = df['price']
    y = df['points']
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    return x, p(x)


x = new_df['price']
y = new_df['points']
plt.scatter(x,y)
fig, ax = plt.subplots()
ax.scatter(x, y, marker='.', alpha=0.1)

z = np.polyfit(x, y, 1)
p = np.poly1d(z)
plt.plot(x,p(x),"r--")

fig_mean, ax_1 = plt.subplots()
ax.plot(x, p(x), "r--")


st.write("Возьмем датасет с вином со всего мира. Оценка вина производится от 80 до 100 баллов. Посмотрим на зависимость набранных баллов от цены бутылки в долларах")

st.pyplot(fig, fig_mean)

price = Slider(title="price", value=100, start=0, end=2500, step=10)

x, y = points_by_price(df, float(price.value))
source = ColumnDataSource(data=dict(x=x, y=y))
plot = figure(height=400, width=400, title="points by price",
              tools="xwheel_pan",
              x_range=[0, 3000], y_range=[80, 100])

plot.line('x', 'y', source=source, line_width=3, line_alpha=0.6)

def update_graph(attrname, old, new):
    x, y = points_by_price(df, float(price.value))
    source.data = dict(x=x, y=y)
price.on_change('value', update_graph)
curdoc().add_root(row(column(price), plot, width=800))
event_result = streamlit_bokeh_events(
        events="Вино по цене",
        bokeh_plot=plot,
        key="foo",
        debounce_time=1000,
    )
st.write(event_result)

coordinates = pd.read_csv('https://raw.githubusercontent.com/zhekaforest/HA/main/world_country_and_usa_states_latitude_and_longitude_values.csv')
del coordinates['usa_state_code']
del coordinates['usa_state_latitude']
del coordinates['usa_state_longitude']
del coordinates['usa_state']


unique_countries = df['country'].dropna().unique()[:-1]

def mean_by_countries(param):
    mean = []
    if param == 'points':
        for country in unique_countries:
            mean.append(df[df['country']==country].points.mean())
    elif param == 'price':
        for country in unique_countries:
            mean.append(df[df['country']==country].price.mean())
    data = {'country': unique_countries, param: mean}
    return pd.DataFrame(data)

st.write('Взглянем на средние значения набранных баллов по странам:')
st.write(mean_by_countries('points'))

st.write("Разместим их на карте таким образом, чтобы большой маркер обозначал более количество набранных баллов")

from streamlit_folium import st_folium
our_mean = mean_by_countries('points')
def show_countries(unique_countries, coordinates, our_mean):
    m = fol.Map(location=[0, 0], zoom_start=1)
    max_mean = float(our_mean['points'].max())
    min_mean = float(our_mean['points'].min())
    for country in unique_countries:
        coordinate = coordinates[coordinates['country'] == country]
        lat = float(coordinate.latitude)
        long = float(coordinate.longitude)
        value = float((our_mean[our_mean['country']==country].points))
        radius = (value - min_mean)/(max_mean - min_mean)*20
        popup_text = 'lala'
        fol.CircleMarker(location=[lat, long], radius=radius, popup=round(value, 2), fill=True).add_to(m)
    return m
our_map = show_countries(unique_countries, coordinates, our_mean)
st_data = st_folium(our_map, width=725)
