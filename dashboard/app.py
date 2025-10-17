import os
from typing import Any, Dict, List, Optional

import requests
import streamlit as st

DEFAULT_BASE_URL = os.getenv("BOOKS_API_BASE_URL", "http://127.0.0.1:8000")


def _api_post(endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
    response = requests.post(endpoint, data=data, timeout=10)
    response.raise_for_status()
    return response.json()


def _api_get(endpoint: str, token: str) -> Any:
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(endpoint, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json()


def authenticate(base_url: str, username: str, password: str) -> Optional[str]:
    try:
        payload = _api_post(
            f"{base_url}/api/v1/auth/token",
            data={"username": username, "password": password},
        )
    except requests.HTTPError as exc:
        st.error(f"Erro ao autenticar: {exc.response.text}")
        return None
    except requests.RequestException as exc:
        st.error(f"Erro de conexão: {exc}")
        return None
    return payload.get("access_token")


def show_overview(base_url: str, token: str) -> None:
    overview = _api_get(f"{base_url}/api/v1/stats/overview", token)
    st.subheader("Visão Geral")
    col1, col2 = st.columns(2)
    col1.metric("Total de Livros", overview.get("total_books", 0))
    col2.metric("Preço Médio", f"£{overview.get('avg_price', 0):.2f}")

    rating_distribution: Dict[str, int] = overview.get("rating_distribution", {})
    if rating_distribution:
        st.bar_chart(rating_distribution, height=250)
    else:
        st.info("Sem dados de avaliação disponíveis.")


def show_categories(base_url: str, token: str) -> None:
    st.subheader("Categorias")
    categories: List[Dict[str, Any]] = _api_get(f"{base_url}/api/v1/stats/categories", token)
    if not categories:
        st.info("Sem dados de categoria disponíveis.")
        return

    category_df = st.dataframe(categories, use_container_width=True)
    st.caption("Estatísticas agregadas por categoria.")
    return category_df


def show_top_books(base_url: str, token: str) -> None:
    st.subheader("Top Rated")
    limit = st.slider("Quantidade", min_value=1, max_value=20, value=5)
    books = _api_get(f"{base_url}/api/v1/books/top-rated?limit={limit}", token)
    if not books:
        st.info("Nenhum livro encontrado.")
        return
    st.table([{k: v for k, v in book.items() if k in {"title", "price", "rating", "category"}} for book in books])


def show_metrics_endpoint(base_url: str) -> None:
    st.subheader("Métricas Prometheus")
    try:
        metrics = requests.get(f"{base_url}/metrics", timeout=10)
        metrics.raise_for_status()
    except requests.RequestException as exc:
        st.error(f"Não foi possível ler /metrics: {exc}")
        return
    st.code(metrics.text[:4000], language="text")


def main() -> None:
    st.set_page_config(page_title="Books API Dashboard", layout="wide")
    st.title("Books API ‒ Monitoramento & Analytics")

    if "token" not in st.session_state:
        st.session_state.token = None

    with st.sidebar:
        st.header("Configurações")
        base_url = st.text_input("Base URL da API", value=DEFAULT_BASE_URL)
        username = st.text_input("Usuário", value=os.getenv("AUTH_USERNAME", "admin"))
        password = st.text_input("Senha", type="password", value=os.getenv("AUTH_PASSWORD", "admin"))

        if st.button("Autenticar"):
            token = authenticate(base_url, username, password)
            if token:
                st.session_state.token = token
                st.success("Autenticado com sucesso!")

        if st.button("Limpar sessão"):
            st.session_state.token = None

        st.markdown("---")
        st.caption("Certifique-se de que a API esteja rodando e o token seja válido.")

    if not st.session_state.token:
        st.info("Informe as credenciais na barra lateral e clique em *Autenticar*.")
        return

    show_overview(base_url, st.session_state.token)
    show_categories(base_url, st.session_state.token)
    show_top_books(base_url, st.session_state.token)
    show_metrics_endpoint(base_url)


if __name__ == "__main__":
    main()
