# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
from flask import Flask

import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn as sk
import io
from ast import literal_eval

import plotly.graph_objs as go

from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
application = app.server
app.title='Literatura Dashboard'

# Carregar DataSets
# Obras
dfobras = pd.read_csv("obrasliterarias.csv", sep='\t', encoding='utf-8')
dfobras = dfobras.drop(columns=['Unnamed: 0','url','words'])

# Emoções e Obras
dfobras_emocoes = pd.read_csv("emocoesdasobras.csv", sep='\t', encoding='utf-8')
dfobras_emocoes['total_emotion'] = dfobras_emocoes['anger'] + dfobras_emocoes['disgust'] + dfobras_emocoes['enjoyment'] + dfobras_emocoes['fear'] + dfobras_emocoes['sadness'] + dfobras_emocoes['surprise']
dfobras_emocoes['anger'] = round( 100 * dfobras_emocoes['anger'] / dfobras_emocoes['total_emotion'], 2)
dfobras_emocoes['disgust'] = round( 100 * dfobras_emocoes['disgust'] / dfobras_emocoes['total_emotion'], 2)
dfobras_emocoes['enjoyment'] = round( 100 * dfobras_emocoes['enjoyment'] / dfobras_emocoes['total_emotion'], 2)
dfobras_emocoes['fear'] = round( 100 * dfobras_emocoes['fear'] / dfobras_emocoes['total_emotion'], 2)
dfobras_emocoes['sadness'] = round( 100 * dfobras_emocoes['sadness'] / dfobras_emocoes['total_emotion'], 2)
dfobras_emocoes['surprise'] = round( 100 * dfobras_emocoes['surprise'] / dfobras_emocoes['total_emotion'], 2)

# Autores
lista_autores = list(dfobras['autor'].unique())
lista_autores.sort()
#lista_autores.insert(0, "Todos")

# Títulos
dfobras_temp = dfobras_emocoes.loc[dfobras_emocoes['autor'] == lista_autores[0]]
lista_titulos = list(dfobras_temp['titulo'].unique())
lista_titulos.sort()

titulos_all = list(dfobras['titulo'].unique())






def convert_options(optionlabels, optionvals):
        return [dict(label=x, value=y) for x, y in zip(optionlabels, optionvals)]


#lista_combo_autores = list()
#item = {'label': 'Todos', 'value': 'Todos'}
#lista_combo_autores.append(item)

#for l in lista_autores:
#    item = {'label': l, 'value': l}
#    lista_combo_autores.append(item)

#print(lista_combo_autores)

#dfobras.loc[dfobras['autor'] == 'Viagens de Gulliver', 'titulo']


def configurar_titulos_emocoes(autor_selecionado):
    dfobras_emocoes_tmp = dfobras_emocoes.loc[dfobras_emocoes['autor'] == autor_selecionado]
    top_labels = ['Alegria', 'Desgosto', 'Medo', 'Raiva', 'Surpresa', 'Tristeza']
    colors = ['rgb(245, 210, 50)',
              'rgb(173, 5, 250)',
              'rgb(25, 150, 44)',
              'rgb(250, 0, 10)',
              'rgb(6, 200, 255)',
              'rgb(10, 10, 255)']

    x_data = dfobras_emocoes_tmp[['enjoyment', 'disgust', 'fear', 'anger', 'surprise', 'sadness']].values.tolist()
    y_data = dfobras_emocoes_tmp['titulo'].values.tolist()

    fig = go.Figure()

    for i in range(0, len(x_data[0])):
        for xd, yd in zip(x_data, y_data):
            fig.add_trace(go.Bar(
                x=[xd[i]], y=[yd],
                orientation='h',
                marker=dict(
                    color=colors[i],
                    line=dict(color='rgb(248, 248, 249)', width=1)
                )
            ))

    fig.update_layout(
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
            domain=[0, 1]
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            zeroline=False,
        ),
        barmode='stack',
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
        margin=dict(l=20, r=10, t=20, b=20),
        showlegend=False,
    )

    annotations = []

    for yd, xd in zip(y_data, x_data):
        # labeling the y-axis
        annotations.append(dict(xref='paper', yref='y',
                                x=0.02, y=yd,
                                xanchor='left',
                                text="<b>" + str(yd) + "</b>",
                                font=dict(family='Arial', size=18,
                                          color='rgb(67, 67, 67)'),
                                showarrow=False, align='right'))
        # labeling the first percentage of each bar (x_axis)
        annotations.append(dict(xref='x', yref='y',
                                x=xd[0] / 2, y=yd,
                                text='',
                                # text=str(xd[0]) + '%',
                                font=dict(family='Arial', size=12,
                                          color='rgb(248, 248, 255)'),
                                showarrow=False))
        # labeling the first Likert scale (on the top)
        if yd == y_data[-1]:
            annotations.append(dict(xref='x', yref='paper',
                                    x=xd[0] / 2, y=1.1,
                                    text='',
                                    # text=top_labels[0],
                                    font=dict(family='Arial', size=12,
                                              color='rgb(67, 67, 67)'),
                                    showarrow=False))
        space = xd[0]
        for i in range(1, len(xd)):
            # labeling the rest of percentages for each bar (x_axis)
            annotations.append(dict(xref='x', yref='y',
                                    x=space + (xd[i] / 2), y=yd,
                                    text='',
                                    # text=str(xd[i]) + '%',
                                    font=dict(family='Arial', size=12,
                                              color='rgb(248, 248, 255)'),
                                    showarrow=False))
            # labeling the Likert scale
            if yd == y_data[-1]:
                annotations.append(dict(xref='x', yref='paper',
                                        x=space + (xd[i] / 2), y=1.1,
                                        text='',
                                        # text=top_labels[i],
                                        font=dict(family='Arial', size=12,
                                                  color='rgb(67, 67, 67)'),
                                        showarrow=False))
            space += xd[i]

    fig.update_layout(annotations=annotations)
    return fig


def configurar_emocoes_da_obra(titulo_selecionado):
    dflinhasFinal = pd.read_csv("obras_grp_emocoes.csv", sep='\t', encoding='utf-8')
    dflinhasExemplo = dflinhasFinal[(dflinhasFinal['titulo'] == titulo_selecionado)]

    titulo_obra = dflinhasExemplo['titulo'].unique()
    autor_obra = dflinhasExemplo['autor'].unique()

    trace_anger = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['anger'].values,
        mode='lines',
        type='scatter',
        name='Raiva',
        line=dict(shape='spline', color='rgb(250, 0, 10)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )
    trace_disgust = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['disgust'].values,
        mode='lines',
        type='scatter',
        name='Desgosto',
        line=dict(shape='spline', color='rgb(173, 5, 250)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )
    trace_enjoyment = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['enjoyment'].values,
        mode='lines',
        type='scatter',
        name='Alegria',
        line=dict(shape='spline', color='rgb(245, 210, 50)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )
    trace_fear = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['fear'].values,
        mode='lines',
        type='scatter',
        name='Medo',
        line=dict(shape='spline', color='rgb(25, 150, 44)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )
    trace_sadness = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['sadness'].values,
        mode='lines',
        type='scatter',
        name='Tristeza',
        line=dict(shape='spline', color='rgb(10, 10, 255)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )
    trace_surprise = dict(
        x=dflinhasExemplo['grp'].values,
        y=dflinhasExemplo['surprise'].values,
        mode='lines',
        type='scatter',
        name='Surpresa',
        line=dict(shape='spline', color='rgb(6, 200, 255)', width=3),
        connectgaps=False
        # ,stackgroup='one'
    )

    titulo_grafico = "Emoções ao Longo da Obra " + titulo_obra + " de " + autor_obra

    # Create layout parameter to assing axes titles and set margins
    layout = dict(
        title=titulo_grafico[0],
        # title="Emoções ao Longo da Obra "+titulo_obra+" de "+autor_obra,
        xaxis=dict(title='Agrupamentos de Linhas'),
        yaxis=dict(title='Emoção do Agrupamento / Emoção Total'),
        width=900,
        height=500,
        margin=dict(
            l=70,
            r=10,
            b=50,
            t=50
        )
    )

    # Compose the final figure
    data = [trace_sadness, trace_enjoyment, trace_anger, trace_fear, trace_disgust, trace_surprise]
    fig = go.Figure(data=data, layout=layout)

    return fig


def configurar_wordcloud(titulo_selecionado):
    dfpalavras = pd.read_csv("palavrasdasobras.csv", sep='\t', encoding='utf-8')
    dfpalavras = dfpalavras.loc[dfpalavras['titulo'] == titulo_selecionado]
    dfpalavras = dfpalavras.drop(columns=['Unnamed: 0'])

    text = df.description[0]

    # Create and generate a word cloud image:
    wordcloud = WordCloud().generate(text)

    # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


titulos_selecionados = list()

app.layout = html.Div([
    
    html.Div([
    html.Label('Autor'),
    dcc.Dropdown(
        #options=[
        #    {'label': 'Todos', 'value': 'Todos'},
        #    {'label': 'Montréal', 'value': 'MTL'},
        #    {'label': 'San Francisco', 'value': 'SF'}
        #],
        id='dropdown_autor',
        options=convert_options(lista_autores, lista_autores),
        value=lista_autores[0]
        #style={'height': '600px', 'width': '350px'}
        #,value='Todos'
    ),
    html.Label('Obra'),
    dcc.Dropdown(
        id='dropdown_titulos',
        #options=convert_options(lista_titulos, lista_titulos),
        value=lista_titulos[0]
        #multi=True
    ),
    dcc.Graph(
        id='graf_titulos_autor'
    )
    ],style={'width': '60%', 'height': '60%', 'display': 'inline-block'}),

    html.Div([
        dcc.Graph(
            id='graf_emocoes_titulo'
        )
    ])

    #html.Div([
    #html.Label('Obra'),
    #dcc.Dropdown(
    #    id='dropdown_titulos',
    #    options=convert_options(lista_titulos, lista_titulos),
    #    value=lista_titulos[0]
    #    #multi=True
    #)  
    #],style={'width': '80%', 'height': '80%', 'display': 'inline-block'})

    #html.Label('Text Input'),
    #dcc.Input(value='MTL', type='text'),

], style={'columnCount': 3})


@app.callback(
    dash.dependencies.Output('dropdown_titulos', 'options'),
    [dash.dependencies.Input('dropdown_autor', 'value')])
def set_titulos_options(autor_selecionado):
    titulos_selecionados = list(dfobras.loc[dfobras['autor'] == autor_selecionado, 'titulo'].unique())
    titulos_selecionados.sort()
    lista_titulos = titulos_selecionados
    return [{'label': i, 'value': i} for i in titulos_selecionados]

@app.callback(
    dash.dependencies.Output('dropdown_titulos', 'value'),
    [dash.dependencies.Input('dropdown_autor', 'value')])
def set_titulos_options(autor_selecionado):
    titulos_selecionados = list(dfobras.loc[dfobras['autor'] == autor_selecionado, 'titulo'].unique())
    titulos_selecionados.sort()
    return titulos_selecionados[0]

@app.callback(
    dash.dependencies.Output('graf_titulos_autor', 'figure'),
    [dash.dependencies.Input('dropdown_autor', 'value')])
def update_titulos_graf(autor_selecionado):
    return configurar_titulos_emocoes(autor_selecionado)


@app.callback(
    dash.dependencies.Output('graf_emocoes_titulo', 'figure'),
    [dash.dependencies.Input('dropdown_titulos', 'value')])
def update_titulos_graf(titulo_selecionado):
    return configurar_emocoes_da_obra(titulo_selecionado)


if __name__ == '__main__':
    app.run_server()
    #app.run_server(debug=True, port=8080)





