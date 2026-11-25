# Deploy do Quimix na Vercel

Fork usado: <https://github.com/Chromick/quimix>

O deploy na Vercel usa **dois projetos**, porque o Docker Compose (Postgres + 3 APIs + Nginx) não roda na Vercel:

1. **API** — FastAPI único (`server.py` na raiz), que junta auth + simulação. Ele também sabe servir o `dist` se ele existir, mas no deploy usamos o projeto web separado.
2. **Web** — Vite/React (`quimix-web`), servido como estático com fallback de SPA.

## 1. Banco de dados

Crie um Postgres gerenciado (Neon, Supabase, Render, etc.). Use um database próprio, por exemplo `quimix_auth`. Guarde a connection string.

> O padrão do código é `sqlite:///./quimix_auth.db`. Isso **não serve na Vercel**: o filesystem é efêmero e a escrita no diretório do projeto não é permitida. Sem `DATABASE_URL`, cadastro/login não vão persistir.

## 2. Projeto da API

- Vercel → **Add New… → Project** → importe <https://github.com/Chromick/quimix>.
- **Root Directory:** `.` (raiz do repo).
- **Framework:** Python / FastAPI (detectado automaticamente).
- **Build Command / Output:** deixe o padrão.
- **Production Branch:** `main`.

Environment Variables (copie os nomes de `vercel-api.env.example`):

| Variável | Valor |
| --- | --- |
| `APP_ENV` | `production` |
| `DATABASE_URL` | `postgresql+psycopg://USUARIO:SENHA@HOST:5432/quimix_auth?sslmode=require` |
| `JWT_SECRET` | string aleatória com 32+ caracteres |
| `CORS_ORIGINS` | URL do projeto da web (ex.: `https://quimix-web-seu-usuario.vercel.app`) |
| `CORS_ORIGIN_REGEX` | `none` para desativar o regex padrão `quimix*.vercel.app` |
| `SEED_ADMIN_ENABLED` | `false` |

Depois de publicar, anote a URL da API (ex.: `https://quimix-api-seu-usuario.vercel.app`) e teste:

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
| `VITE_API_BASE_URL` | URL do projeto da API, sem barra no final |

Modelo em `quimix-web/.env.production.example`.

## 4. Ordem recomendada

1. Criar o Postgres.
2. Publicar a **API** e copiar a URL.
3. Publicar a **Web** com `VITE_API_BASE_URL` apontando para essa URL.
4. Adicionar a URL da Web em `CORS_ORIGINS` na API e fazer um **Redeploy** da API.
5. Testar cadastro → login → simulação.

## 5. Ajustes já feitos neste fork

- `quimix-web/src/api/client.ts`: removido o fallback fixo para `https://quimix-api.vercel.app` (hoje fora do ar) e adicionado erro claro quando `VITE_API_BASE_URL` não é configurado.
- `server.py`: `CORS_ORIGINS` e `CORS_ORIGIN_REGEX` passam a ser lidos de variáveis de ambiente; o comportamento antigo (`localhost:5173`, `quimix.vercel.app`, regex `quimix*.vercel.app`) continua como padrão.
- `vercel-api.env.example` e `quimix-web/.env.production.example`: modelos de configuração.

## 6. Observações

- `quimix.vercel.app` e `quimix-api.vercel.app` **não devem ser reutilizados**: hoje o primeiro serve outro app e o segundo responde 404. Use os domínios que a Vercel te der ou configure domínios próprios.
- O `docker-compose` local continua funcionando normalmente; nada foi mudado nele.
- Para atualizar o fork com o upstream (uma vez): `git remote add upstream https://github.com/LuanaPZenha/quimix.git`. Depois: `git fetch upstream && git merge upstream/main`.
