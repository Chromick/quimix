# Deploy do Quimix na Vercel

Fork usado: <https://github.com/Chromick/quimix>

O deploy na Vercel usa **dois projetos**, porque o Docker Compose (Postgres + 3 APIs + Nginx) não roda na Vercel:

1. **API** — FastAPI único (`server.py` na raiz), que junta auth + simulação. Ele também sabe servir o `dist` se ele existir, mas no deploy usamos o projeto web separado.
2. **Web** — Vite/React (`quimix-web`), servido como estático com fallback de SPA.

Projeto de referência: `quimix-api-chromick` (API) e `quimix-web-chromick` (web).

## 1. Banco de dados

A versão original traz suporte a **Turso/libSQL** no `quimix-auth-service`:

- `TURSO_DATABASE_URL` — ex.: `libsql://quimix-auth-<org>.turso.io`
- `TURSO_AUTH_TOKEN` — token de acesso do banco

Quando as duas variáveis estão preenchidas, o `database.py` monta a URL `sqlite+libsql://...?secure=true` e usa o token. Sem elas, cai no `DATABASE_URL` padrão (`sqlite:///./quimix_auth.db`), que **não serve na Vercel** (filesystem efêmero).

> As credenciais usadas no deploy vieram do `Quimix.zip` da pasta Downloads (`quimix-infra/.env`).

## 2. Projeto da API

- Vercel → **Add New… → Project** → importe <https://github.com/Chromick/quimix>.
- **Root Directory:** `.` (raiz do repo).
- **Entrypoint:** `api/index.py` importa o `app` do `server.py`; `vercel.json` reescreve todas as rotas para `/api/index`.
- **Framework:** Python / FastAPI (detectado automaticamente).
- **Build Command / Output:** deixe o padrão.
- **Production Branch:** `main`.

Environment Variables (modelo em `vercel-api.env.example`):

| Variável | Valor |
| --- | --- |
| `APP_ENV` | `production` |
| `TURSO_DATABASE_URL` | URL `libsql://...` do banco de auth |
| `TURSO_AUTH_TOKEN` | token do Turso |
| `JWT_SECRET` | string aleatória com 32+ caracteres |
| `CORS_ORIGINS` | `https://quimix-web-chromick.vercel.app` |
| `CORS_ORIGIN_REGEX` | `none` |
| `SEED_ADMIN_ENABLED` | `false` |

Depois de publicar, teste:

- `GET /health` → `{"status":"ok","service":"quimix"}`
- `GET /docs` → OpenAPI

## 3. Projeto da Web

- Vercel → **Add New… → Project** → importe o **mesmo fork**.
- **Root Directory:** `quimix-web`.
- **Framework:** Vite (detectado automaticamente).
- **Build Command:** `npm run build`.
- **Output Directory:** `dist`.
- **Production Branch:** `main`.

Environment Variable **de build** (ela é embutida no JS, então precisa existir antes do build):

| Variável | Valor |
| --- | --- |
| `VITE_API_BASE_URL` | `https://quimix-api-chromick.vercel.app` |

Modelo em `quimix-web/.env.production.example`.

## 4. Ordem recomendada

1. Publicar a **API** com as variáveis do item 2.
2. Publicar a **Web** com `VITE_API_BASE_URL` apontando para a API.
3. Conferir `CORS_ORIGINS` na API e fazer redeploy se necessário.
4. Testar cadastro → login → simulação.

## 5. Ajustes já feitos neste fork

- `quimix-web/src/api/client.ts`: removido o fallback fixo para `https://quimix-api.vercel.app` (hoje fora do ar) e adicionado erro claro quando `VITE_API_BASE_URL` não é configurado.
- `server.py`: `CORS_ORIGINS` e `CORS_ORIGIN_REGEX` passam a ser lidos de variáveis de ambiente; o comportamento antigo continua como padrão.
- `api/index.py` + `vercel.json`: entrypoint Python exigido pela Vercel (`api/`) e rewrite de todas as rotas para a API.
- `quimix-auth-service/app/config.py` e `app/infrastructure/database.py`: suporte a Turso/libSQL trazido da versão original (`Quimix.zip`).
- `requirements.txt`: adicionado `sqlalchemy-libsql==0.2.0`.
- `quimix-auth-service/tests/unit/test_turso_url.py`: testes da conversão de URL Turso.
- `vercel-api.env.example` e `quimix-web/.env.production.example`: modelos de configuração.

## 6. Observações

- `quimix.vercel.app` e `quimix-api.vercel.app` **não devem ser reutilizados**: hoje o primeiro serve outro app e o segundo responde 404. Use os domínios que a Vercel te der ou configure domínios próprios.
- O `docker-compose` local continua funcionando normalmente; nada foi mudado nele.
- Para atualizar o fork com o upstream (uma vez): `git remote add upstream https://github.com/LuanaPZenha/quimix.git`. Depois: `git fetch upstream && git merge upstream/main`.
