import streamlit as st
import requests
import feedparser
from datetime import datetime

# Configuração da página no Streamlit
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# 🔍 URL do RSS do Google Notícias para "Reforma Ministerial"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=reforma+ministerial&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# Inicializar histórico se ainda não existir
if "news_history" not in st.session_state:
    st.session_state.news_history = []

# Função para buscar notícias do RSS do Google News
def fetch_google_news_rss():
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    results = []

    for entry in feed.entries:
        result = {
            "title": entry.title,
            "link": entry.link,
            "snippet": entry.summary,
            "source": entry.source.title if "source" in entry else "Google News",
            "publishedAt": datetime(*entry.published_parsed[:6]).strftime("%d/%m/%Y %H:%M"),
        }

        # Evitar duplicatas no histórico
        if result["link"] not in [news["link"] for news in st.session_state.news_history]:
            st.session_state.news_history.append(result)

    return results

# Exibir notícias no Streamlit
def display_news(articles):
    for article in articles:
        st.markdown(f"### {article['title']}")
        st.write(article["snippet"])
        st.write(f"Fonte: {article['source']}")
        st.write(f"[Leia mais]({article['link']})")
        st.write("Publicado em:", article["publishedAt"])
        st.markdown("---")

# Sidebar para configurações
st.sidebar.header("Configurações")
refresh_rate = st.sidebar.slider("Taxa de atualização (segundos)", 60, 600, 120)

# Título principal
st.title("📢 Monitor de Notícias: Reforma Ministerial")
st.info(f"Monitorando notícias diretamente do **Google Notícias** via RSS.")

# Buscar notícias e atualizar histórico
articles = fetch_google_news_rss()

# Exibir histórico completo
display_news(st.session_state.news_history)





