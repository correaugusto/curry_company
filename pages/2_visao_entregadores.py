# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(
    page_title="Visão Entregadores",
    page_icon="None",
    layout='wide',
    initial_sidebar_state="expanded"
)

#-----------------------------------------
# Funções
#-----------------------------------------

def top_delivers(df1, top_asc):
    df2 = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
              .groupby(['City','Delivery_person_ID'])
              .mean()
              .sort_values(['Time_taken(min)','City'], ascending = top_asc)
              .reset_index())

    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
                
    df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index(drop=True)
    return df3


def clean_code(df1):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remocao dos espaços das variaveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
           
    """
    #1. convertendo a coluna Delivery_person_Age de texto 'object' para número 'int'
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    #2. convertendo a coluna Ratings de texto para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #3. convertendo a coluna 'Order_Date' de texto para data, usando o comando 'pd.to_datetime'
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    #4. convertendo multiple_deliveries de texto para int
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5 . removendo os espações dentro de strings/texto/object
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:,'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:,'City'].str.strip()

    # 6. Limpando a coluna de time taken - Comando para remover o texto de números
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )
    
    return df1

#-----------------------------------Inicio da estrutura lógica do código-----------------------------------
#-----------------------------------
# Import dataset
#-----------------------------------
df = pd.read_csv(r'C:\Users\User\Documents\repos\FTC\dataset\train.csv')
#-----------------------------------
#Limpando os dados
df1 = clean_code( df )

#=====================================
# Barra lateral
#=====================================
st.header('Marketplace - Visão Entregadores')

#image_path = r'C:\Users\User\Documents\repos\FTC\logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image(image, width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYY')

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'Hight', 'Jam'],
    default = ['Low', 'Medium', 'Hight', 'Jam'])

st.sidebar.markdown("""___""")

weather_conditions = st.sidebar.multiselect(
    'Quais as condições do clima?',
    ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'],
    default = ['Cloudy', 'Fog', 'Sandstorms', 'Stormy', 'Sunny', 'Windy'])

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data
linhas_selecionas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionas, :]

#filtro de transito - isni(está em...)
linhas_selecionas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionas, :]
df1 = df1.reset_index( drop=True )

#=====================================
# Layout no Streamlit
#=====================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns(4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade ) 
            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            # A melhor condição de veículos
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )

        with col4:
        # A pior condição de veículo
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condicao', pior_condicao )
    
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação media por Entregador')
            df_avg_ratings_per_deliver = (df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
            
        with col2:
            st.markdown('##### Avaliação media por transito')
            df_avg_std_ratings_by_traffic = ((df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                                 .groupby('Road_traffic_density')
                                                 .agg({'Delivery_person_Ratings':['mean','std']}))
                                                 .reset_index())
            st.dataframe( df_avg_std_ratings_by_traffic )
            
            st.markdown('##### Avaliação media por clima')
            df_avg_std_ratings_by_weather = ((df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                                 .groupby('Weatherconditions')
                                                 .agg({'Delivery_person_Ratings':['mean','std']}))
                                                 .reset_index())
            st.dataframe( df_avg_std_ratings_by_weather ) 
    
    
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top Entregadores mais rapidos')
            df3 = top_delivers(df1, top_asc=True)
            st.dataframe( df3 )
        with col2:
            df3 = top_delivers(df1, top_asc=False)
            st.markdown('##### Top Entregadores mais lentos')
            st.dataframe( df3 )