import streamlit as st
import requests
import feedparser
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
import pytz

# Fuso horário do Brasil
BRASIL_TZ = pytz.timezone("America/Sao_Paulo")

# Configuração da página no Streamlit
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# 🔍 URL do RSS do Google Notícias para "Reforma Ministerial"
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q=reforma+ministerial&hl=pt-BR&gl=BR&ceid=BR:pt-419"

# Inicializar histórico se ainda não existir
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

# 🔹 Buscar a data real do site da notícia original
def fetch_real_publication_date(news_url):
    try:
        response = requests.get(news_url, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            date_patterns = [
                {"tag": "time", "attr": "datetime"},
                {"tag": "meta", "attr": "content", "name": "article:published_time"},
                {"tag": "meta", "attr": "content", "name": "datePublished"},
                {"tag": "span", "class": "publish-date"},
                {"tag": "div", "class": "date"},
            ]

            for pattern in date_patterns:
                if "name" in pattern:
                    date_element = soup.find(pattern["tag"], {"name": pattern["name"]})
                else:
                    date_element = soup.find(pattern["tag"], class_=pattern.get("class"))

                if date_element and date_element.has_attr(pattern["attr"]):
                    raw_date = date_element[pattern["attr"]]
                    try:
                        return datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=pytz.utc).astimezone(BRASIL_TZ)
                    except ValueError:
                        continue

        return None
    except Exception:
        return None

# 🔹 Buscar notícias do RSS do Google News
def fetch_google_news_rss():
    feed = feedparser.parse(GOOGLE_NEWS_RSS)
    results = []

    for entry in feed.entries:
        published_at = None
        published_str = "Data não disponível"

        if hasattr(entry, "published"):
            relative_date = entry.published
            converted_date = convert_relative_time(relative_date)

            if converted_date:
                published_at = converted_date
            else:
                try:
                    published_at = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z").replace(tzinfo=pytz.utc).astimezone(BRASIL_TZ)
                except ValueError:
                    published_str = entry.published

            if published_at:
                published_str = published_at.strftime("%d/%m/%Y %H:%M")

        real_date = fetch_real_publication_date(entry.link)
        if real_date:
            published_at = real_date
            published_str = real_date.strftime("%d/%m/%Y %H:%M")

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

        if result["link"] not in [news["link"] for news in st.session_state.news_history]:
            st.session_state.news_history.append(result)

    # ✅ Correção: Garantir que `news_history` é uma lista antes de ordenar
    if not isinstance(st.session_state.news_history, list):
        st.session_state.news_history = []

    # ✅ Correção: Garantir que cada item tem `publishedAt_datetime`
    for news in st.session_state.news_history:
        if "publishedAt_datetime" not in news:
            news["publishedAt_datetime"] = datetime.min

    # ✅ Correção: Ordenar corretamente evitando `NoneType` error
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
        st.write(f"🕒 **Publicado em:** {article['publishedAt']}")
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



