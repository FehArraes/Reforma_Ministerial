import streamlit as st
import requests
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

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
        # Corrigir a data de publicação
        published_at = None
        published_str = "Data não disponível"

        if hasattr(entry, "published"):
            try:
                # Tentar diferentes formatos de data
                possible_formats = [
                    "%a, %d %b %Y %H:%M:%S %Z",  # Formato padrão do Google News
                    "%Y-%m-%dT%H:%M:%SZ",       # Formato ISO
                    "%d/%m/%Y %H:%M",           # Formato já convertido
                ]
                for fmt in possible_formats:
                    try:
                        published_at = datetime.strptime(entry.published, fmt)
                        published_str = published_at.strftime("%d/%m/%Y %H:%M")
                        break
                    except ValueError:
                        continue
            except Exception:
                published_str = entry.published  # Se der erro, mantém o valor original

        # Corrigir a descrição removendo HTML
        raw_snippet = entry.summary
        clean_snippet = BeautifulSoup(raw_snippet, "html.parser").get_text()

        result = {
            "title": entry.title,
            "link": entry.link,
            "snippet": clean_snippet,  # Agora a descrição é apenas texto puro
            "source": entry.source.title if "source" in entry else "Google News",
            "publishedAt": published_str,
        }

        # Adiciona a chave apenas se a data for válida
        if published_at:
            result["publishedAt_datetime"] = published_at

        # Evitar duplicatas no histórico
        if result["link"] not in [news["link"] for news in st.session_state.news_history]:
            st.session_state.news_history.append(result)

    # Ordenar as notícias da mais recente para a mais antiga, ignorando as que não têm data
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


