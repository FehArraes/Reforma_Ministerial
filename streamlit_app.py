import streamlit as st
import requests
from datetime import datetime

# Configuração da página no Streamlit
st.set_page_config(page_title="Monitor de Reforma Ministerial", layout="wide")

# 🗝️ Chaves da API do Google
GOOGLE_API_KEY = "AIzaSyAwPi4OhimTFHKiHtb2NOAIgRicmwco8Y0"  # Substitua pela sua API Key
SEARCH_ENGINE_ID = "f00a0d98e7d4c4cb9"  # Substitua pelo seu Search Engine ID

# 🔍 Busca mais abrangente para evitar restrições
SEARCH_TERM = '"reforma ministerial"'  # Remove 'intitle:' para aumentar os resultados

# Inicializar histórico se ainda não existir
if "news_history" not in st.session_state:
    st.session_state.news_history = []

# Função para buscar notícias no Google Custom Search
def fetch_google_news(api_key, search_engine_id, query, num_results=10):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={search_engine_id}&key={api_key}&num={num_results}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        results = []

        for item in data.get("items", []):
            result = {
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", "Sem descrição disponível"),
                "source": item["displayLink"],
                "publishedAt": datetime.now().strftime("%d/%m/%Y %H:%M")
            }

            # Evitar duplicatas no histórico
            if result["link"] not in [news["link"] for news in st.session_state.news_history]:
                st.session_state.news_history.append(result)

        return results
    else:
        st.error(f"Erro ao buscar notícias: {response.status_code}")
        return []

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
st.info(f"Monitorando notícias relacionadas a **'{SEARCH_TERM}'** via Google News.")

# Buscar notícias e atualizar histórico
articles = fetch_google_news(GOOGLE_API_KEY, SEARCH_ENGINE_ID, SEARCH_TERM)

# Exibir histórico completo
display_news(st.session_state.news_history)




