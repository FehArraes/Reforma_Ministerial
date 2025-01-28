import streamlit as st
import requests
from datetime import datetime

# Configurações da página
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# Chave da API NewsAPI
API_KEY = "f3df2dfd4d7d4f85b1b15290491e4604"

# Termos fixos a serem monitorados
SEARCH_TERM = "reforma ministerial OR articulação ministerial OR reforma do governo"

# Função para buscar notícias da API
def fetch_news(api_key, query, page_size=100):
    url = f"https://newsapi.org/v2/everything?q={query}&pageSize={page_size}&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        articles = data.get("articles", [])
        # Ordenar artigos do mais recente para o mais antigo
        articles = sorted(
            articles,
            key=lambda x: datetime.strptime(x["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
            reverse=True
        )
        return articles
    else:
        st.error(f"Erro ao buscar notícias: {response.status_code}")
        return []

# Exibir notícias no Streamlit
def display_news(articles, search_term):
    for article in articles:
        title = article["title"] or ""
        description = article["description"] or ""
        
        # Filtrar notícias que contenham o termo no título ou descrição
        if any(term.lower() in title.lower() or term.lower() in description.lower() for term in search_term.split(" OR ")):
            st.markdown(f"### {title}")
            st.write(description or "Sem descrição disponível")
            st.write(f"Fonte: {article['source']['name']}")
            st.write(f"[Leia mais]({article['url']})")
            st.write("Publicado em:", datetime.strptime(article["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d/%m/%Y %H:%M"))
            st.markdown("---")

# Sidebar para configurações
st.sidebar.header("Configurações")
refresh_rate = st.sidebar.slider("Taxa de atualização (segundos)", 10, 300, 60)

# Título principal
st.title("Monitor de Notícias: Reforma Ministerial")
st.info(f"Monitorando notícias relacionadas a **'{SEARCH_TERM}'**...")

# Buscar notícias e exibir
articles = fetch


