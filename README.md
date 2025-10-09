# Tech Challenge — Books API (FastAPI)

API pública para consulta de livros extraídos de [books.toscrape.com](https://books.toscrape.com/).Inclui **web scraping**, **pipeline de dados**, **API REST**, **documentação (Swagger)**, **deploy** e **testes**.

## ⚙️ Arquitetura

```
Scraper (requests + BeautifulSoup)
      ↓
Transform (pandas) → CSV em `data/books.csv`
      ↓
FastAPI (endpoints REST) + Swagger
      ↓
Consumidores (cientistas de dados / serviços)
```

## 📦 Estrutura

```
api/
  main.py
  routes/
    books.py
    categories.py
    stats.py
  models/
    book_model.py
scripts/
  scraper.py
  transform.py
data/
  books.csv         # gerado pelo scraper
tests/
  test_api.py
Procfile
Dockerfile
requirements.txt
README.md
```

## 🚀 Como rodar localmente

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# (1) Rodar scraping (gera data/books.csv)
python scripts/scraper.py

# (2) Subir a API
uvicorn api.main:app --reload
```

Acesse Swagger: http://127.0.0.1:8000/docs

## 🌐 Deploy (Render/Heroku/Fly.io)

- Faça push para o GitHub.
- No Render/Heroku: crie um serviço web apontando para este repo.
- `Procfile` já define: `web: uvicorn api.main:app --host 0.0.0.0 --port $PORT`.

## 📚 Endpoints

- `GET /api/v1/health`
- `GET /api/v1/books`
- `GET /api/v1/books/{id}`
- `GET /api/v1/books/search?title=&category=`
- `GET /api/v1/categories`
- `GET /api/v1/stats/overview`
- `GET /api/v1/stats/categories`
- `GET /api/v1/books/top-rated`
- `GET /api/v1/books/price-range?min=&max=`

## 🧪 Testes

```bash
pytest -q
```

## 🔮 Próximos Passos (ML-Ready)

- Trocar CSV por Postgres ou MongoDB.
- Adicionar endpoints `/api/v1/ml/*` e autenticação JWT.
- Monitoramento (logs estruturados, métricas) e dashboard (Streamlit).
