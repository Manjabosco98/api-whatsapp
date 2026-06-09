# Evolution API + Webhook FastAPI

Projeto para rodar a Evolution API com Postgres, Redis e uma API própria em FastAPI para receber webhooks de eventos do WhatsApp.

## O que existe neste projeto

- `docker-compose.yaml`: sobe Postgres, Redis, Evolution API e a API de webhook.
- `.env`: variáveis da Evolution API.
- `webhook-api/main.py`: API FastAPI que recebe eventos em `POST /webhook/evolution`.
- `webhook-api/.env`: variáveis da API de webhook.
- `webhook-api/logs/`: payloads recebidos pelos webhooks, salvos em JSON.

## Antes de subir para o GitHub

Não envie arquivos com dados sensíveis ou logs de produção.

Confira se estes itens estão ignorados pelo Git:

```gitignore
.env
webhook-api/.env
webhook-api/logs/
```

Se algum `.env` já tiver sido enviado para o repositório, gere novas chaves/senhas antes do deploy.

## Variáveis que você precisa alterar

### `.env` da Evolution API

Edite o arquivo `.env` da raiz e ajuste principalmente:

```env
SERVER_TYPE=http
SERVER_PORT=8080
SERVER_URL=https://SUA-EVOLUTION-API.onrender.com

AUTHENTICATION_API_KEY=SUA_CHAVE_FORTE

DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=postgresql://USUARIO:SENHA@HOST:PORTA/BANCO
DATABASE_CONNECTION_CLIENT_NAME=evolution

CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=redis://HOST:PORTA
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=true
CACHE_LOCAL_ENABLED=false

CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome

LOG_LEVEL=INFO
```

### URLs para ambiente local

No ambiente local com `docker-compose`, use os nomes dos serviços Docker:

```env
DATABASE_CONNECTION_URI=postgresql://evolution:evolution@postgres:5432/evolution
CACHE_REDIS_URI=redis://redis:6379
SERVER_URL=http://localhost:8080
```

### URLs no Render manual

No Render, como você vai criar um serviço por vez, copie as URLs internas que o próprio Render mostrar para Postgres e Redis:

```env
DATABASE_CONNECTION_URI=URL_INTERNA_DO_POSTGRES
CACHE_REDIS_URI=URL_INTERNA_DO_REDIS
SERVER_URL=https://api-whatsapp.onrender.com
```

Se o Render gerar outro nome para a Evolution API, altere `SERVER_URL` para a URL real.

Exemplo visual:

```text
Evolution API publica:
https://minha-evolution-api.onrender.com

Webhook publico:
https://minha-webhook-api.onrender.com/webhook/evolution

Postgres interno:
copiado do serviço Postgres

Redis interno:
copiado do serviço Key Value
```

### `webhook-api/.env`

Edite `webhook-api/.env` e ajuste:

```env
APP_NAME=Evolution Webhook API
EVOLUTION_INSTANCE_NAME=NOME_DA_SUA_INSTANCIA
WHATSAPP_GROUP_JID=ID_DO_GRUPO@g.us
```

O `WHATSAPP_GROUP_JID` é opcional. Se preencher, a API só tratará mensagens desse grupo. Se deixar vazio, ela registra todos os eventos recebidos.

## Rodando localmente

Com Docker instalado:

```bash
docker compose up -d --build
```

Serviços locais:

- Evolution API: `http://localhost:8080`
- Webhook FastAPI: `http://localhost:8000`
- Health check do webhook: `GET http://localhost:8000/`
- Endpoint do webhook: `POST http://localhost:8000/webhook/evolution`

Para parar:

```bash
docker compose down
```

Para parar e apagar volumes locais:

```bash
docker compose down -v
```

## Configurando o webhook na Evolution API

Depois que a Evolution API estiver rodando, configure o webhook da instância para apontar para:

```text
https://SUA-WEBHOOK-API.onrender.com/webhook/evolution
```

Localmente, use:

```text
http://webhook-api:8000/webhook/evolution
```

ou, se estiver testando fora da rede Docker:

```text
http://localhost:8000/webhook/evolution
```

Eventos que a API já trata:

- `MESSAGES_UPSERT`
- `CHATS_UPSERT`
- `CHATS_UPDATE`
- `GROUPS_UPSERT`
- `GROUP_UPDATE`
- `GROUP_PARTICIPANTS_UPDATE`

Todos os payloads recebidos são salvos em `webhook-api/logs/`.

## Deploy no Render

Como o Blueprint com disco persistente exige plano pago, suba os recursos um por um dentro do seu projeto no Render.

Referências oficiais:

- Docker no Render: https://render.com/docs/docker
- Deploy de imagem Docker pronta: https://render.com/docs/deploying-an-image
- Variáveis de ambiente no Render: https://render.com/docs/configure-environment-variables

### 1. Criar PostgreSQL

No Render:

```text
New > Postgres
```

Nome recomendado:

```text
api-whatsapp-postgres
```

Depois de criar, copie a URL interna do banco. Ela será usada na variável:

```env
DATABASE_CONNECTION_URI=URL_INTERNA_DO_POSTGRES
```

### 2. Criar Redis

No Render:

```text
New > Key Value
```

Nome recomendado:

```text
api-whatsapp-redis
```

Depois de criar, copie a URL interna do Redis. Ela será usada na variável:

```env
CACHE_REDIS_URI=URL_INTERNA_DO_REDIS
```

### 3. Criar Evolution API

No Render:

```text
New > Web Service
```

Escolha a opção para usar imagem Docker pronta e informe:

```text
docker.io/evoapicloud/evolution-api:latest
```

Nome recomendado:

```text
api-whatsapp
```

Configure as variáveis de ambiente:

```env
SERVER_TYPE=http
SERVER_PORT=10000
PORT=10000
SERVER_URL=https://api-whatsapp.onrender.com

AUTHENTICATION_API_KEY=SUA_CHAVE_FORTE

DATABASE_ENABLED=true
DATABASE_PROVIDER=postgresql
DATABASE_CONNECTION_URI=URL_INTERNA_DO_POSTGRES
DATABASE_CONNECTION_CLIENT_NAME=evolution

DATABASE_SAVE_DATA_INSTANCE=true
DATABASE_SAVE_DATA_NEW_MESSAGE=true
DATABASE_SAVE_MESSAGE_UPDATE=true
DATABASE_SAVE_DATA_CONTACTS=true
DATABASE_SAVE_DATA_CHATS=true
DATABASE_SAVE_DATA_LABELS=true
DATABASE_SAVE_DATA_HISTORIC=true

CACHE_REDIS_ENABLED=true
CACHE_REDIS_URI=URL_INTERNA_DO_REDIS
CACHE_REDIS_PREFIX_KEY=evolution
CACHE_REDIS_SAVE_INSTANCES=true
CACHE_LOCAL_ENABLED=false

DEL_INSTANCE=false

CONFIG_SESSION_PHONE_CLIENT=Evolution API
CONFIG_SESSION_PHONE_NAME=Chrome

LOG_LEVEL=INFO
```

Se o Render gerar outro endereço para o serviço, ajuste:

```env
SERVER_URL=https://URL-REAL-DA-EVOLUTION-API.onrender.com
```

### 4. Criar Webhook API

No Render:

```text
New > Web Service
```

Conecte o repositório do GitHub e configure:

- Nome: `api-whatsapp-webhook`
- Runtime: Docker
- Root Directory: `webhook-api`
- Dockerfile Path: `Dockerfile`
- Health Check Path: `/`

Configure as variáveis:

```env
APP_NAME=Evolution Webhook API
EVOLUTION_INSTANCE_NAME=NOME_DA_SUA_INSTANCIA
WHATSAPP_GROUP_JID=
```

O `webhook-api/Dockerfile` usa a variável `PORT` do Render e mantém `8000` como fallback local:

```dockerfile
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

### 5. Configurar webhook na Evolution API

Depois que os dois serviços estiverem online, configure o webhook da instância para:

```text
https://api-whatsapp-webhook.onrender.com/webhook/evolution
```

Se o Render criar outro endereço para o webhook, use o endereço real mantendo o caminho:

```text
https://URL-REAL-DO-WEBHOOK.onrender.com/webhook/evolution
```

### Observação importante

Sem disco persistente pago na Evolution API, sessões/instâncias podem ser perdidas em restart ou redeploy. Para testar e validar o fluxo, tudo bem. Para produção estável, o ideal é usar disco persistente ou outro armazenamento suportado.

## Checklist antes do deploy

- Subir o projeto no GitHub.
- Conferir se `.env`, `webhook-api/.env` e `webhook-api/logs/` não foram enviados.
- Conferir se o nome `api-whatsapp` está disponível no Render.
- Conferir se o nome `api-whatsapp-webhook` está disponível no Render.
- Criar Postgres e copiar a URL interna para `DATABASE_CONNECTION_URI`.
- Criar Redis e copiar a URL interna para `CACHE_REDIS_URI`.
- Criar a Evolution API usando a imagem Docker oficial.
- Criar o webhook usando o Dockerfile em `webhook-api`.
- Configurar na Evolution API o webhook apontando para `/webhook/evolution`.
