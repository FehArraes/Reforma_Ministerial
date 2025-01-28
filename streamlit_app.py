import streamlit as st
import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

# Configuração da página no Streamlit
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# 🔍 URL do RSS do Google Notícias para "Reforma Ministerial"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=reforma+ministerial&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# Inicializar histórico se ainda não existir
if "news_history" not in st.session_state:
    st.session_state.news_history = []

# Função para converter datas relativas para absolutas
def convert_relative_time(relative_time):
    now = datetime.now()
    
    # Expressões regulares para detectar tempo relativo
    match = re.search(r"(\d+)\s+min", relative_time)
    if match:
        return now - timedelta(minutes=int(match.group(1)))

    match = re.search(r"(\d+)\s+hora", relative_time)
    if match:
        return now - timedelta(hours=int(match.group(1)))

    match = re.search(r"(\d+)\s+dia", relative_time)
    if match:
        return now - timedelta(days=int(match.group(1)))

    if "ontem" in relative_time.lower():
        return now - timedelta(days=1)

    return None  # Caso não seja uma data relativa

# Função para buscar notícias do RSS do Google News
def fetch_google_news_rss():
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    results = []

    for entry in feed.entries:
        # Corrigir a data de publicação
        published_at = None
        published_str = "Data não disponível"

        if hasattr(entry, "published"):
            relative_date = entry.published
            converted_date = convert_relative_time(relative_date)

            if converted_date:
                published_at = converted_date
            else:
                try:
                    published_at = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                except ValueError:
                    published_str = entry.published  # Se não for possível converter, manter o original

            if published_at:
                published_str = published_at.strftime("%d/%m/%Y %H:%M")

        # Corrigir a descrição removendo HTML
        raw_snippet = entry.summary
        clean_snippet = BeautifulSoup(raw_snippet, "html.parser").get_text()

        result = {
            "title": entry.title,
            "link": entry.link,
            "snippet": clean_snippet,
            "source": entry.source.title if "source" in entry else "Google News",
            "publishedAt": published_str,
        }

        if published_at:
            result["publishedAt_datetime"] = published_at

        # Evitar duplicatas no histórico
        if result["link"] not in [news["link"] for news in st.session_state.news_history]:
            st.session_state.news_history.append(result)

    # Ordenar as notícias da mais recente para a mais antiga
    st.session_state.news_history.sort(
        key=lambda x: x.get("publishedAt_datetime", datetime.min),
        reverse=True
    )

    return st.session_state.news_history

# Exibir notícias no Streamlit
def display_news(articles):
    for article in articles:
        st.markdown(f"### {article['title']}")
        st.write(f"📰 {article['snippet']}")
        st.write(f"📌 **Fonte:** {article['source']}")
        st.write(f"🕒 **Publicado em:** {article['publishedAt']}")
        st.write(f"🔗 [Leia mais]({article['link']})")
        st.markdown("---")

# Sidebar para configurações
st.sidebar.header("Configurações")
refresh_rate = st.sidebar.slider("Taxa de atualização (segundos)", 60, 600, 120)

# Título principal
st.title("📢 Monitor de Notícias: Reforma Ministerial")
st.info(f"Monitorando notícias diretamente do **Google Notícias** via RSS.")

# Buscar notícias e atualizar histórico
articles = fetch_google_news_rss()

# Exibir histórico completo (já ordenado)
display_news(articles)

