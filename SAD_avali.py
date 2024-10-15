import pandas as pd
import streamlit as st
import json

tmdb_data = pd.read_csv('tmdb_5000_movies.csv')
imdb_data = pd.read_csv('imdb_top_1000.csv')

# Mesclar os DataFrames com base em uma coluna comum
merged_data = pd.merge(tmdb_data, imdb_data, left_on='original_title', right_on='Series_Title', how='inner')

columns_to_drop = ['Poster_Link', 'Series_Title']
for column in columns_to_drop:
    if column in merged_data.columns:
        merged_data = merged_data.drop(columns=[column])

# Função para extrair gêneros do JSON
def extract_genres(genres_json):
    genres_list = json.loads(genres_json.replace("'", '"'))
    return [genre['name'] for genre in genres_list]

merged_data['genres'] = merged_data['genres'].apply(extract_genres)

st.title('Análise de Filmes TMDB e IMDB')

st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para", ["Página 1", "Página 2"])

all_genres = set([genre for sublist in merged_data['genres'] for genre in sublist])
genre_filter = st.sidebar.multiselect('Filtrar por Gênero', all_genres)

if genre_filter:
    filtered_data = merged_data[merged_data['genres'].apply(lambda x: any(genre in x for genre in genre_filter))]
else:
    filtered_data = merged_data

if page == "Página 1":
    st.header('Página 1: Análise Geral')

    st.subheader('Distribuição de Avaliações IMDB')
    imdb_rating_counts = filtered_data['IMDB_Rating'].value_counts().sort_index()
    st.bar_chart(imdb_rating_counts)

    st.subheader('Receita vs. Orçamento')
    st.scatter_chart(filtered_data[['budget', 'revenue']])

    st.subheader('Avaliações IMDB vs. Avaliações TMDB')
    st.scatter_chart(filtered_data[['IMDB_Rating', 'vote_average']])

    st.subheader('Popularidade vs. Número de Votos')
    st.scatter_chart(filtered_data[['popularity', 'vote_count']])
    st.dataframe(filtered_data[['original_title', 'popularity', 'vote_count']])

    st.subheader('Receita vs. Avaliações IMDB')
    st.bar_chart(filtered_data.groupby('IMDB_Rating')['revenue'].mean())

    st.subheader('Top 10 Filmes por Popularidade')
    top_10_popular = filtered_data.nlargest(10, 'popularity')
    st.table(top_10_popular[['original_title', 'popularity', 'IMDB_Rating', 'vote_average']])

    st.subheader('Total de Votos')
    total_votes = filtered_data['vote_count'].sum()
    st.metric(label="Total de Votos", value=total_votes)

elif page == "Página 2":
    st.header('Página 2: Análise de Gêneros')

    st.subheader('Distribuição de Gêneros')
    genres = filtered_data['genres'].explode().value_counts()
    st.bar_chart(genres)

    st.subheader('Avaliação Média por Gênero')
    genre_ratings = filtered_data.explode('genres').groupby('genres')['IMDB_Rating'].mean().sort_values(ascending=False)
    st.bar_chart(genre_ratings)

    st.subheader('Filmes por Gênero')
    st.dataframe(filtered_data[['original_title', 'genres', 'IMDB_Rating', 'vote_average']])

    st.subheader('Total de Filmes')
    total_movies = filtered_data['original_title'].nunique()
    st.metric(label="Total de Filmes", value=total_movies)
