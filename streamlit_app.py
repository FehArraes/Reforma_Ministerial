import streamlit as st
import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import pytz

# 🔹 Fuso horário do Brasil
BRASIL_TZ = pytz.timezone("America/Sao_Paulo")

# 🔹 Configuração da página no Streamlit
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# 🔍 URL do RSS do Google Notícias para "Reforma Ministerial"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=reforma+ministerial&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# 🔹 Inicializar histórico se ainda não existir
if "news_history" not in st.session_state:
    st.session_state.news_history = []

# 🔹 Converter tempo relativo para absoluto
def convert_relative_time(relative_time):
    now = datetime.now(BRASIL_TZ)

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

    return None

# 🔹 Classificar o tempo relativo igual ao Google Notícias
def format_relative_time(published_at):
    now = datetime.now(BRASIL_TZ)
    diff = now - published_at

    if diff < timedelta(minutes=60):
        return f"{int(diff.total_seconds() / 60)} minutos atrás"
    elif diff < timedelta(hours=24):
        return f"{int(diff.total_seconds() / 3600)} horas atrás"
    elif diff < timedelta(days=2):
        return "Ontem"
    else:
        return f"{published_at.strftime('%d de %B de %Y')}"

# 🔹 Buscar notícias do RSS do Google News
def fetch_google_news_rss():
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    results = []

    for entry in feed.entries:
        published_at = None
        relative_str = "Data não disponível"

        if hasattr(entry, "published"):
            relative_date = entry.published
            converted_date = convert_relative_time(relative_date)

            if converted_date:
                published_at = converted_date
            else:
                try:
                    published_at = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=pytz.utc).astimezone(BRASIL_TZ)
                except ValueError:
                    relative_str = entry.published

            if published_at:
                relative_str = format_relative_time(published_at)

        raw_snippet = entry.summary
        clean_snippet = BeautifulSoup(raw_snippet, "html.parser").get_text()

        result = {
            "title": entry.title,
            "link": entry.link,
            "snippet": clean_snippet,
            "source": entry.source.title if "source" in entry else "Google News",
            "publishedAt_relative": relative_str,  # 📌 Agora usando tempo relativo
        }

        if published_at:
            result["publishedAt_datetime"] = published_at

        if result["link"] not in [news["link"] for news in st.session_state.news_history]:
            st.session_state.news_history.append(result)

    # ✅ Correção: Garantir que `news_history` é uma lista antes de ordenar
    if not isinstance(st.session_state.news_history, list):
        st.session_state.news_history = []

    # ✅ Correção: Garantir que cada item tem `publishedAt_datetime`
    for news in st.session_state.news_history:
        if "publishedAt_datetime" not in news:
            news["publishedAt_datetime"] = datetime.min

    # ✅ Correção: Ordenar corretamente os mais recentes primeiro
    try:
        st.session_state.news_history.sort(
            key=lambda x: x["publishedAt_datetime"],
            reverse=True
        )
    except Exception as e:
        st.error(f"Erro ao ordenar as notícias: {e}")

    return st.session_state.news_history

# 🔹 Exibir notícias no Streamlit
def display_news(articles):
    for article in articles:
        st.markdown(f"### {article['title']}")
        st.write(f"📰 {article['snippet']}")
        st.write(f"📌 **Fonte:** {article['source']}")
        st.write(f"🕒 **Publicado:** {article['publishedAt_relative']}")
        st.write(f"🔗 [Leia mais]({article['link']})")
        st.markdown("---")

# 🔹 Sidebar para configurações
st.sidebar.header("Configurações")
refresh_rate = st.sidebar.slider("Taxa de atualização (segundos)", 60, 600, 120)

# 🔹 Título principal
st.title("📢 Monitor de Notícias: Reforma Ministerial")
st.info(f"Monitorando notícias diretamente do **Google Notícias** via RSS.")

# 🔹 Buscar notícias e atualizar histórico
articles = fetch_google_news_rss()

# 🔹 Exibir histórico completo (já ordenado)
display_news(articles)


