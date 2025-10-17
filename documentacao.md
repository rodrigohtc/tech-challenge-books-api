# Books API — Documentação Completa

## 📌 Visão Geral

A **Books API** entrega um pipeline completo para coletar, transformar e expor dados de livros do site [books.toscrape.com](https://books.toscrape.com/). O projeto cobre scraping, transformação para CSV, API REST com FastAPI, autenticação via JWT, monitoramento (logs estruturados, métricas Prometheus) e um dashboard de analytics em Streamlit.

### Objetivos

- **Consolidar dados** em um formato fácil de consumir por analistas e serviços.
- **Prover uma API REST segura** para consultas filtradas, estatísticas e busca.
- **Oferecer monitoramento** via logs estruturados e métricas de desempenho.
- **Disponibilizar um dashboard** simples para visualização dos indicadores principais.

## 🏗️ Arquitetura & Fluxo

```
Scraper (requests + BeautifulSoup)
      ↓
Transform (pandas) → CSV em data/books.csv
      ↓
FastAPI (endpoints REST) + JWT + Swagger
      ↓
Monitoramento (Prometheus / logs)
      ↓
Dashboard Streamlit
```

## 🔧 Configuração & Execução

### 1. Preparar ambiente

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Definir credenciais e segredo JWT

```bash
export AUTH_USERNAME=admin
export AUTH_PASSWORD=admin
export JWT_SECRET_KEY=troque-por-uma-chave-secreta
```

> Dica: crie um arquivo `.env.local` com as variáveis e carregue com `set -a && source .env.local && set +a`.

### 3. Gerar dados

```bash
python scripts/scraper.py
```

- Salva `data/books.csv` com título, categoria, preço, rating, disponibilidade e links.

### 4. Subir a API

```bash
uvicorn api.main:app --reload
```

- Swagger disponível em `http://127.0.0.1:8000/docs`.
- Métricas Prometheus em `http://127.0.0.1:8000/metrics`.
- Logs estruturados no stdout.

### 5. Rodar dashboard (opcional)

```bash
streamlit run dashboard/app.py
```

- Informe a base URL (`http://127.0.0.1:8000`), usuário e senha no menu lateral.
- Visualize overview (total de livros, preço médio), distribuição de ratings, estatísticas por categoria, top-rated dinamicamente e snapshot do endpoint `/metrics`.

### 6. Rodar API e dashboard juntos

- Duas abas de terminal:
  - `uvicorn api.main:app --reload`
  - `streamlit run dashboard/app.py`
- Ou, em um único terminal (Unix/macOS):
  ```bash
  uvicorn api.main:app --reload & streamlit run dashboard/app.py
  ```

## 🔒 Autenticação

- Endpoint: `POST /api/v1/auth/token`
- Content-Type: `application/x-www-form-urlencoded`
- Campos: `username`, `password`

Exemplo `curl`:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

- Resposta: `{"access_token": "...", "token_type": "bearer", "expires_in": 1800}`
- Use o token nas chamadas protegidas com `Authorization: Bearer <token>`.
- Apenas `GET /api/v1/health` é público.

## 📚 Endpoints

| Método | Caminho | Descrição | Auth |
|--------|--------|-----------|------|
| GET | `/api/v1/health` | Status da API | Não |
| POST | `/api/v1/auth/token` | Gera token JWT | Não |
| GET | `/api/v1/books` | Lista paginada (`skip`, `limit`) | Sim |
| GET | `/api/v1/books/{id}` | Livro por ID | Sim |
| GET | `/api/v1/books/search` | Filtros: `title`, `category`, `min_price`, etc. | Sim |
| GET | `/api/v1/books/top-rated` | Top N livros por rating/price | Sim |
| GET | `/api/v1/books/price-range` | Livros dentro de um intervalo de preço | Sim |
| GET | `/api/v1/categories` | Lista de categorias únicas | Sim |
| GET | `/api/v1/stats/overview` | Total de livros, preço médio, distribuição de rating | Sim |
| GET | `/api/v1/stats/categories` | Estatísticas agregadas por categoria | Sim |
| GET | `/api/v1/ml/features` | Features limpas para consumo por modelos | Sim |
| GET | `/api/v1/ml/training-data` | Dataset completo + metadados para treinamento | Sim |
| POST | `/api/v1/ml/predictions` | Recebe predições geradas externamente | Sim |
| GET | `/metrics` | Métricas Prometheus | Não (ideal expor só internamente) |

### Endpoints de Insights

- `GET /api/v1/stats/overview`: estatísticas gerais da coleção (total de livros, preço médio, distribuição de ratings).
- `GET /api/v1/stats/categories`: estatísticas detalhadas por categoria (quantidade de livros, preços por categoria).
- `GET /api/v1/books/top-rated`: livros com melhor avaliação (rating mais alto).
- `GET /api/v1/books/price-range?min={min}&max={max}`: filtra livros em uma faixa de preço específica.

### Endpoints de ML

- `GET /api/v1/ml/features`: retorna lista com colunas `category`, `price`, `rating`, `in_stock` e `title`, ideal para enriquecer features.
- `GET /api/v1/ml/training-data`: devolve registros completos, array de colunas de features e target sugerido (`price`), facilitando pipelines de treino.
- `POST /api/v1/ml/predictions`: envia resultados produzidos por modelos; a API responde com resumo (quantidade recebida, modelos distintos, média de score).

## 📊 Monitoramento

- **Logs estruturados** (`api/middleware/logging.py`)
  - Emite JSON no stdout por requisição (`event`, método, path, status, tempo, IP).
  - Facilita ingestão por Loki, ELK, Datadog, etc.
- **Métricas** (`prometheus-fastapi-instrumentator`)
  - Contadores por método/status, histogramas de latência, número de exceções.
  - Endpoint `/metrics` pronto para Prometheus/Grafana.

## 📋 Testes

- Suite em `tests/test_api.py`.

```bash
pytest -q
```

- Adapte/expanda conforme adicionar features.

## 🚀 Deploy

- Projeto pronto para renderização em Render, Heroku ou Fly.io.
- `Procfile` define `web: uvicorn api.main:app --host 0.0.0.0 --port $PORT`.
- Ajuste variáveis de ambiente (AUTH_*, JWT_*).
- Para monitoramento em produção, combine `/metrics` com Prometheus ou serviços gerenciados.
- Deploy atual no Render:
  - API: https://tech-challenge-books-api-cdgc.onrender.com
  - Dashboard: https://tech-challenge-books-api-rhtc-dashboard.onrender.com

## 🔮 Próximos Passos

- Migrar dados de CSV para banco (Postgres/Mongo).
- Criar endpoints de Machine Learning.
- Integrar alertas com base nas métricas (ex.: tempo de resposta).
- Automatizar scraping e transformação com jobs agendados.

---

> Qualquer dúvida ou sugestão de melhoria, abra uma issue ou contribua com PRs! 🎉
