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

### URLs no Render com Blueprint

Com o `render.yaml`, você não precisa montar manualmente a URL do banco nem do Redis.

O Render injeta estas variáveis automaticamente:

```env
DATABASE_CONNECTION_URI=URL_INTERNA_DO_POSTGRES_GERADA_PELO_RENDER
CACHE_REDIS_URI=URL_INTERNA_DO_REDIS_GERADA_PELO_RENDER
```

Você só precisa conferir a URL pública da Evolution API:

```env
SERVER_URL=https://api-whatsapp.onrender.com
```

Se você mudar o nome do serviço no `render.yaml`, altere `SERVER_URL` para combinar.

Exemplo visual:

```text
Evolution API publica:
https://minha-evolution-api.onrender.com

Webhook publico:
https://minha-webhook-api.onrender.com/webhook/evolution

Postgres interno:
gerado automaticamente pelo Render

Redis interno:
gerado automaticamente pelo Render
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

O projeto já tem um `render.yaml` na raiz. Esse arquivo funciona como um Blueprint do Render e cria tudo junto:

- Evolution API (`api-whatsapp`)
- Webhook API (`api-whatsapp-webhook`)
- PostgreSQL (`api-whatsapp-postgres`)
- Redis (`api-whatsapp-redis`)

Referências oficiais:

- Blueprints no Render: https://render.com/docs/infrastructure-as-code
- Blueprint YAML: https://render.com/docs/blueprint-spec
- Docker no Render: https://render.com/docs/docker
- Deploy de imagem Docker pronta: https://render.com/docs/deploying-an-image
- Variáveis de ambiente no Render: https://render.com/docs/configure-environment-variables

### Forma mais simples

No Render, use:

```text
New > Blueprint
```

Depois selecione o repositório do GitHub que contém este projeto.

O Render vai ler o arquivo:

```text
render.yaml
```

e criar os serviços automaticamente.

### URLs que você talvez precise alterar

No `render.yaml`, deixei estes nomes:

```yaml
name: api-whatsapp
name: api-whatsapp-webhook
name: api-whatsapp-postgres
name: api-whatsapp-redis
```

Com esses nomes, as URLs públicas esperadas ficam assim:

```text
Evolution API:
https://api-whatsapp.onrender.com

Webhook API:
https://api-whatsapp-webhook.onrender.com

Endpoint do webhook:
https://api-whatsapp-webhook.onrender.com/webhook/evolution
```

Se o Render não aceitar algum nome porque já existe, troque no `render.yaml`:

```yaml
name: api-whatsapp
```

por algo único, por exemplo:

```yaml
name: minha-evolution-api
```

Nesse caso, altere também:

```env
SERVER_URL=https://minha-evolution-api.onrender.com
```

### Banco e Redis

Você não precisa montar manualmente a URL do banco nem do Redis no Blueprint.

O `render.yaml` já faz isso automaticamente:

```yaml
DATABASE_CONNECTION_URI:
  fromDatabase:
    name: api-whatsapp-postgres
    property: connectionString

CACHE_REDIS_URI:
  fromService:
    type: keyvalue
    name: api-whatsapp-redis
    property: connectionString
```

Ou seja:

- Local com Docker: usa `postgres` e `redis`.
- Render com Blueprint: o Render injeta as URLs automaticamente.

### Variáveis que ainda pode ajustar

Depois que o Blueprint criar tudo, confira no painel do Render:

- `SERVER_URL`: deve ser a URL pública da Evolution API, por padrão `https://api-whatsapp.onrender.com`.
- `AUTHENTICATION_API_KEY`: o Render gera automaticamente, mas você pode trocar.
- `EVOLUTION_INSTANCE_NAME`: nome da instância que você vai usar.
- `WHATSAPP_GROUP_JID`: preencha somente se quiser filtrar um grupo específico.

### Configurar webhook

Depois do deploy, configure na Evolution API o webhook:

```text
https://api-whatsapp-webhook.onrender.com/webhook/evolution
```

Se você mudou o nome do serviço do webhook, siga o formato:

```text
https://NOME-DO-SERVICO-WEBHOOK.onrender.com/webhook/evolution
```

### Observação sobre armazenamento

O serviço `api-whatsapp` usa disco persistente em:

```text
/evolution/instances
```

Isso mantém as instâncias/sessões da Evolution API mesmo após restart.

## Porta no Render

O `render.yaml` configura a Evolution API na porta `10000`, que é o padrão esperado por Web Services do Render:

```text
SERVER_PORT=10000
PORT=10000
```

O `webhook-api/Dockerfile` usa a variável `PORT` do Render e mantém `8000` como fallback local:

```dockerfile
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

## Checklist antes do deploy

- Subir o projeto no GitHub.
- Conferir se `.env`, `webhook-api/.env` e `webhook-api/logs/` não foram enviados.
- Conferir se o nome `api-whatsapp` está disponível no Render.
- Conferir se o nome `api-whatsapp-webhook` está disponível no Render.
- Conferir se os nomes `api-whatsapp-postgres` e `api-whatsapp-redis` estão disponíveis no Render.
- Se trocar o nome da Evolution API, alterar `SERVER_URL` no `render.yaml`.
- Criar o Blueprint no Render usando o `render.yaml`.
- Configurar na Evolution API o webhook apontando para `/webhook/evolution`.
