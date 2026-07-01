# Kapitour

Aplicativo mobile de turismo para **Maricá (RJ)**, desenvolvido com **React Native / Expo** no frontend e **FastAPI** em arquitetura de **microserviços** no backend. O visitante explora pontos turísticos, rotas, mapa interativo, cupons de parceiros e o sistema gamificado **KapiPass** (XP, carimbos, missões, conquistas e rankings).

---

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Stack tecnológica](#stack-tecnológica)
- [Arquitetura geral](#arquitetura-geral)
- [Microserviços backend](#microserviços-backend)
- [Clean Architecture e padrões](#clean-architecture-e-padrões)
- [Frontend (app mobile)](#frontend-app-mobile)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Pré-requisitos](#pré-requisitos)
- [Configuração](#configuração)
- [Como executar](#como-executar)
- [API Gateway e rotas](#api-gateway-e-rotas)
- [Referência da API](#referência-da-api)
- [Autenticação (JWT)](#autenticação-jwt)
- [Banco de dados](#banco-de-dados)
- [Testes (TDD / BDD)](#testes-tdd--bdd)
- [Usuários de demonstração](#usuários-de-demonstração)
- [Testes manuais com cURL](#testes-manuais-com-curl)
- [Solução de problemas](#solução-de-problemas)
- [Migração Supabase → SQLite](#migração-supabase--sqlite)
- [Licença](#licença)

---

## Sobre o projeto

O **Kapitour** é uma plataforma de turismo digital focada em Maricá. O app permite:

- Descobrir **pontos turísticos** e **rotas** organizadas por categorias
- Visualizar locais no **mapa** com geolocalização
- **Favoritar** pontos e **avaliar** experiências
- Resgatar **cupons** de parceiros locais
- Participar do **KapiPass**: check-in em pontos, carimbos digitais, missões, conquistas, ranking e diário de viagem

O backend foi evoluído de um monolito FastAPI para **cinco microserviços independentes**, cada um com seu próprio banco SQLite, expostos por um **API Gateway** (nginx) na porta **8000**. O app mobile continua consumindo a mesma URL base: `http://localhost:8000/api`.

---

## Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| **Autenticação** | Cadastro, login, perfil e JWT |
| **Conteúdo** | Categorias, pontos turísticos, rotas e relações ponto↔categoria |
| **Engajamento** | Favoritos, avaliações e média por ponto |
| **Commerce** | Produtos, estoque, campanhas e resgate de cupons |
| **KapiPass** | XP, níveis, check-in, carimbos, missões, conquistas, eco-pass, diário, tesouros e ranking |
| **Acessibilidade** | TTS, botão flutuante e contexto de acessibilidade no app |
| **Clima** | Tela de previsão do tempo integrada |

---

## Stack tecnológica

### Frontend (mobile)

| Tecnologia | Uso |
|------------|-----|
| React Native 0.81 + Expo 54 | App multiplataforma (Android / iOS / Web) |
| React Navigation 7 | Navegação por abas e stack |
| Axios | Cliente HTTP para a API |
| AsyncStorage / SecureStore | Persistência local |
| Jest + jest-expo | Testes unitários dos casos de uso |

### Backend (microserviços)

| Tecnologia | Uso |
|------------|-----|
| Python 3.11 + FastAPI | API REST de cada microserviço |
| SQLAlchemy 2 | ORM e persistência |
| SQLite3 | Banco por domínio (um arquivo `.db` por serviço) |
| Redis 7 | Cache, sessões, blacklist JWT, rate limiting, broker Celery |
| Celery + Flower | Filas assíncronas e monitoramento de workers |
| Argon2 + bcrypt | Hash de senhas (Argon2 novo, bcrypt legado) |
| python-jose | JWT access + refresh tokens |
| Prometheus client | Métricas HTTP em `/api/metrics` |
| nginx | API Gateway (roteamento `/api/*`) |
| Docker Compose | Orquestração local dos serviços |
| pytest + pytest-bdd | Testes unitários, integração e cenários BDD (Gherkin PT) |

---

## Arquitetura geral

```mermaid
flowchart TB
    subgraph Cliente
        APP[App Expo / React Native]
    end

    subgraph Gateway
        NGINX[nginx :8000]
    end

    subgraph Microservicos
        AUTH[auth]
        CONTENT[content]
        ENG[engagement]
        COMM[commerce]
        KAPI[kapipass]
    end

    subgraph Bancos
        DB1[(auth.db)]
        DB2[(content.db)]
        DB3[(engagement.db)]
        DB4[(commerce.db)]
        DB5[(kapipass.db)]
    end

    APP -->|HTTP /api/*| NGINX
    NGINX --> AUTH
    NGINX --> CONTENT
    NGINX --> ENG
    NGINX --> COMM
    NGINX --> KAPI

    AUTH --> DB1
    CONTENT --> DB2
    ENG --> DB3
    COMM --> DB4
    KAPI --> DB5

    ENG -.->|HTTP interno| CONTENT
    KAPI -.->|HTTP interno| AUTH
    KAPI -.->|HTTP interno| CONTENT
```

**Fluxo típico de uma requisição:**

1. O app envia `GET http://localhost:8000/api/pontos-turisticos`
2. O nginx encaminha para o container **content**
3. O serviço consulta `content.db` e retorna JSON
4. Para favoritos enriquecidos, **engagement** chama **content** internamente para buscar dados dos pontos

---

## Microserviços backend

| Serviço | Container | Responsabilidade | Banco |
|---------|-----------|------------------|-------|
| **auth** | `kapitour-auth` | Registro, login, perfil, usuários internos | `auth.db` |
| **content** | `kapitour-content` | Categorias, pontos, rotas | `content.db` |
| **engagement** | `kapitour-engagement` | Favoritos e avaliações | `engagement.db` |
| **commerce** | `kapitour-commerce` | Produtos, estoque, cupons | `commerce.db` |
| **kapipass** | `kapitour-kapipass` | Gamificação completa | `kapipass.db` |
| **gateway** | `kapitour-gateway` | Proxy reverso único na porta 8000 | — |
| **redis** | `kapitour-redis` | Cache, sessões, blacklist JWT, rate limit, broker Celery | volume `redis_data` |
| **worker** | `kapitour-worker` | Tarefas assíncronas (e-mail, QR, KapiPass, logs) | — |
| **flower** | `kapitour-flower` | Monitor Celery (UI) | porta **5555** |

Cada microserviço expõe:

- `GET /api/health` — health check (banco + Redis)
- `GET /api/status` — status detalhado (banco, Redis, workers)
- `GET /api/metrics` — métricas Prometheus
- Documentação Swagger em `/docs` **dentro do container** (não exposta pelo gateway)

### Comunicação entre serviços

Serviços que precisam de dados de outros domínios usam clientes HTTP em `backend/shared/kapitour_shared/clientes_http.py`, autenticados com `INTERNAL_SERVICE_KEY`:

| Serviço | Depende de | Motivo |
|---------|------------|--------|
| engagement | content | Enriquecer favoritos com nome/coordenadas dos pontos |
| kapipass | auth, content | Validar usuário e obter dados de pontos no check-in |

Variáveis de ambiente (Docker Compose):

```env
AUTH_SERVICE_URL=http://auth:8000
CONTENT_SERVICE_URL=http://content:8000
ENGAGEMENT_SERVICE_URL=http://engagement:8000
COMMERCE_SERVICE_URL=http://commerce:8000
KAPIPASS_SERVICE_URL=http://kapipass:8000
INTERNAL_SERVICE_KEY=kapitour-internal-dev-key
```

---

## Clean Architecture e padrões

Cada microserviço segue **Clean Architecture** com camadas em português:

```
backend/services/{servico}/app/
├── dominio/              # Entidades, portas, casos de uso, regras, estratégias, eventos
├── infraestrutura/       # ORM, repositórios SQLAlchemy
├── aplicacao/            # Orquestração (ex.: kapipass)
├── apresentacao/         # Roteadores FastAPI, esquemas Pydantic, dependências
├── main.py
└── migracoes.py          # create_all + seed inicial
```

**Princípios e padrões aplicados:**

| Conceito | Onde aparece |
|----------|--------------|
| **SRP / DIP** | Casos de uso recebem repositórios e clientes via injeção (`Depends`) |
| **OCP** | Cadeia de validação de cupons (`commerce`) e estratégias de missão/conquista (`kapipass`) |
| **Strategy** | Progresso de missões por `visitados` ou `carimbos` |
| **Observer** | Eventos de check-in publicam atualização de XP/conquistas |
| **Repository** | Repositórios SQLAlchemy implementam portas do domínio |
| **Clean Code** | Nomes, pastas e contratos em português |

O monolito legado permanece em `backend/app/` para compatibilidade (`docker compose --profile monolith`).

### Infraestrutura compartilhada (`backend/shared/kapitour_shared/`)

Camada transversal de produção reutilizada por todos os microserviços:

```
backend/shared/kapitour_shared/
├── core/           # App factory, logging estruturado, health/metrics
├── cache/          # Cliente Redis + cache-aside
├── security/       # JWT, Argon2, RBAC, sanitização
├── middleware/     # Request ID, timing, rate limit, headers OWASP, erros
├── queues/         # Configuração Celery
├── workers/        # Tarefas assíncronas
└── events/         # Auditoria centralizada (login, logout, alterações)
```

**Factory de aplicação:** todos os microserviços usam `criar_aplicacao()` que registra middlewares, CORS, compressão GZip e rotas de monitoramento automaticamente.

---

## Frontend (app mobile)

### Camadas

```
lib/
├── api/                    # Infraestrutura HTTP (axios, endpoints por domínio)
│   ├── cliente-http.js     # Cliente base + token em memória
│   ├── autenticacao.js
│   ├── turismo.js
│   ├── kapipass.js
│   └── cupons.js
├── infraestrutura/         # Reexporta lib/api (adaptadores)
├── aplicacao/
│   └── casos-de-uso/       # Lógica de aplicação (sem HTTP nas telas)
│       └── autenticacao.js
└── api.js                  # Barrel + aliases legados (authApi, dbApi, …)

hooks/
└── useAuth.js              # Contexto de autenticação (AuthProvider / useAuth)
```

**Aliases mantidos por compatibilidade:** `authApi`, `dbApi`, `kapipassApi`, `cuponsApi`, `AuthProvider`, `useAuth`.

### Telas principais

| Tela | Função |
|------|--------|
| `Home`, `PontosTuristicos`, `Rotas`, `Mapa` | Exploração turística |
| `Login`, `Cadastro`, `AreaUsuario` | Conta do usuário |
| `Cupons`, `LeitorQR` | Commerce e cupons |
| `KapiPassScreen` + sub-telas | Gamificação (carimbos, missões, ranking, etc.) |
| `WeatherScreen` | Clima |
| `Contato` | Informações de contato |

---

## Estrutura do repositório

```
app_kapitour_test/
├── App.js                      # Entrada do app + navegação
├── Screens/                    # Telas React Native
├── components/                 # Componentes reutilizáveis
├── hooks/                      # Hooks (useAuth, etc.)
├── lib/                        # API, casos de uso, infraestrutura
├── __tests__/                  # Testes Jest (frontend)
├── backend/
│   ├── shared/kapitour_shared/ # JWT, Redis, Celery, middleware, RBAC, cache
│   ├── services/
│   │   ├── auth/app/
│   │   ├── content/app/
│   │   ├── engagement/app/
│   │   ├── commerce/app/
│   │   └── kapipass/app/
│   ├── gateway/nginx.conf      # Roteamento do API Gateway
│   ├── scripts/
│   │   ├── split_database.py   # Migra monolito → bancos separados
│   │   └── run_tests.py        # Executa pytest por microserviço
│   ├── app/                    # Monolito legado (opcional)
│   ├── conftest.py
│   ├── pytest.ini
│   ├── requirements.txt
│   └── requirements-dev.txt
├── database/                   # auth.db, content.db, … (volume Docker)
├── docker-compose.yml
├── Dockerfile                  # Imagem do monolito legado
├── jest.config.js
├── package.json
└── .env                        # Variáveis de ambiente (não commitar segredos reais)
```

---

## Pré-requisitos

| Ferramenta | Versão mínima | Finalidade |
|------------|---------------|------------|
| [Docker](https://www.docker.com/) + Docker Compose | recente | Backend (recomendado) |
| [Node.js](https://nodejs.org/) | 18+ | App mobile |
| npm ou yarn | — | Dependências JS |
| [Expo Go](https://expo.dev/go) ou emulador | — | Executar o app |
| Python 3.11+ | — | Testes backend locais (opcional) |

Para desenvolvimento mobile nativo: Android Studio e/ou Xcode conforme a plataforma alvo.

---

## Configuração

Crie ou edite o arquivo `.env` na **raiz do projeto**:

```env
# Backend (monolito legado / referência)
DATABASE_URL=sqlite:///database/kapitour.db
JWT_SECRET=kapitour-dev-secret-change-in-production
INTERNAL_SERVICE_KEY=kapitour-internal-dev-key
CORS_ORIGINS=*

# App mobile — URL do API Gateway
EXPO_PUBLIC_API_URL=http://localhost:8000/api
```

### URL da API por ambiente

| Ambiente | Configuração |
|----------|----------------|
| **Expo Web / simulador iOS** | `EXPO_PUBLIC_API_URL=http://localhost:8000/api` (padrão do `.env.example`) |
| **Emulador Android** | Detectado automaticamente (`10.0.2.2:8000`) |
| **Celular físico (Expo Go)** | **Automático** — IP e porta vêm do Metro; a API passa pelo proxy na mesma porta do QR code (ex.: `:8081`) |

> **Equipe:** não é necessário editar IP no `.env` ao trocar de máquina ou rede Wi‑Fi. Copie `.env.example` → `.env` e use `localhost`.

### Setup rápido para a equipe (celular + PC)

**Pré-requisitos:** [Docker Desktop](https://www.docker.com/), Node 18+, [Expo Go](https://expo.dev/go) no celular, PC e celular na **mesma Wi‑Fi**.

```bash
git clone <repo>
cd app_kapitour_test-main
cp .env.example .env          # Linux/macOS
# copy .env.example .env      # Windows
npm install
```

**Terminal 1 — backend:**

```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts/dev.ps1

# macOS / Linux
chmod +x scripts/dev.sh && ./scripts/dev.sh
```

**Terminal 2 — app:**

```bash
npm start                     # ja usa --lan
```

No celular: escaneie o QR code no **modo LAN** (não use Tunnel). No terminal do Expo deve aparecer:

`[Kapitour] API via Metro (porta 8081): http://<IP>:8081/api`

**Login teste:** `user@kapitour.com` / `user123`

| Problema | Solução |
|----------|---------|
| `ERR_NETWORK` no celular | Reinicie com `npx expo start --lan --clear`; confira Docker (`docker compose ps`) |
| Modo Tunnel no Expo | Troque para **LAN** — Tunnel não alcança API local |
| Porta 8000 ocupada | O gateway tenta 8000 e 8080 automaticamente |
| Windows: firewall | Execute uma vez como Admin: `scripts\abrir-firewall-api.bat` |

> **Importante:** altere `JWT_SECRET` e `INTERNAL_SERVICE_KEY` em produção.

---

## Como executar

### Opção 1 — Docker Compose (recomendado)

Sobe os 5 microserviços + gateway nginx:

```bash
docker compose up --build
```

Endpoints após subir:

| Recurso | URL |
|---------|-----|
| API Gateway | http://localhost:8000 |
| Health check | http://localhost:8000/api/health |

Os bancos SQLite ficam em `./database/` (montados como volume).

**Parar os containers:**

```bash
docker compose down
```

### Migrar banco monolito → microserviços

Se você já possui `database/kapitour.db` do monolito:

```bash
python backend/scripts/split_database.py
docker compose up --build
```

O script copia tabelas para `auth.db`, `content.db`, `engagement.db`, `commerce.db` e `kapipass.db`.

### Monolito legado (opcional)

```bash
docker compose --profile monolith up kapitour-monolith --build
```

Usa `database/kapitour.db` e expõe tudo em uma única API FastAPI na porta 8000.

### Opção 2 — Backend local (sem Docker)

Instale dependências e rode **um** microserviço por vez (exemplo: auth):

```bash
pip install -r backend/requirements.txt
set PYTHONPATH=backend\shared;backend\services\auth
set DATABASE_URL=sqlite:///database/auth.db
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Repita para os demais serviços em portas distintas ou use apenas Docker para o backend.

### App mobile (Expo)

```bash
npm install
npm start          # modo LAN (padrao) — necessario para celular fisico
```

Comandos úteis:

```bash
npm run android    # Emulador/dispositivo Android
npm run ios        # Simulador iOS (macOS)
npm run web        # Navegador
npm run start:tunnel   # Apenas se precisar de Tunnel (API local NAO funciona)
```

Em **celular físico**, o app conecta à API via **proxy do Metro** (mesma porta do bundler). Não é preciso atualizar IP no `.env` ao mudar de computador ou rede.

Certifique-se de que o backend Docker está rodando (`docker compose ps`).

---

## API Gateway e rotas

O nginx (`backend/gateway/nginx.conf`) roteia prefixos `/api/*` para o microserviço correto:

| Prefixo `/api/...` | Microserviço |
|--------------------|--------------|
| `auth`, `usuarios`, `internal/usuarios` | auth |
| `categorias`, `pontos-turisticos`, `ponto-categoria`, `rotas`, `rota-ponto`, `internal/pontos` | content |
| `favoritos`, `avaliacoes`, `ponto-avaliacoes` | engagement |
| `produtos`, `tipos-produto`, `estoque`, `cupons` | commerce |
| `kapipass` | kapipass |
| `health` | resposta estática do gateway |

---

## Referência da API

Todas as rotas abaixo são acessadas via gateway: `http://localhost:8000/api/...`

### Auth

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| POST | `/auth/register` | Cadastro de usuário | Não |
| POST | `/auth/login` | Login (retorna JWT) | Não |
| GET | `/auth/me` | Perfil do usuário logado | JWT |
| GET | `/usuarios/email-exists?email=` | Verifica e-mail disponível | Não |
| PATCH | `/usuarios/{auth_id}` | Atualiza perfil | JWT |

### Content

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/categorias` | Lista categorias |
| GET | `/pontos-turisticos` | Lista pontos (filtro opcional por categoria) |
| GET | `/pontos-turisticos/{id}` | Detalhe de um ponto |
| GET | `/rotas` | Lista rotas |
| GET | `/rotas/{id}/pontos` | Pontos de uma rota |
| GET | `/ponto-categoria` | Relações ponto ↔ categoria |
| GET | `/rota-ponto` | Relações rota ↔ ponto |

### Engagement

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/favoritos` | Favoritos do usuário (com dados do ponto) | JWT |
| POST | `/favoritos` | Adiciona favorito | JWT |
| DELETE | `/favoritos` | Remove favorito | JWT |
| GET | `/avaliacoes` | Lista avaliações | JWT |
| POST | `/avaliacoes` | Cria ou atualiza avaliação | JWT |
| PUT | `/avaliacoes/{id}` | Atualiza avaliação | JWT |
| GET | `/ponto-avaliacoes/media?ponto_id=` | Média de notas do ponto | Não |

### Commerce

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/produtos` | Lista produtos |
| GET | `/tipos-produto` | Tipos de produto |
| GET | `/estoque` | Estoque |
| GET | `/cupons/disponiveis` | Cupons disponíveis |
| GET | `/cupons/resgatados/{usuario_id}` | Cupons já resgatados |
| POST | `/cupons/resgatar` | Resgata cupom |
| GET | `/cupons/campanhas-parceiro/{parceiro_id}` | Campanhas do parceiro |

### KapiPass

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| GET | `/kapipass/me` | Perfil gamificado (XP, nível) | JWT |
| GET | `/kapipass/niveis` | Tabela de níveis | Não |
| POST | `/kapipass/checkin` | Check-in geolocalizado em ponto | JWT |
| GET | `/kapipass/carimbos` | Carimbos do usuário | JWT |
| GET | `/kapipass/conquistas` | Conquistas | JWT |
| GET | `/kapipass/missoes` | Missões disponíveis | JWT |
| POST | `/kapipass/missoes/{id}/aceitar` | Aceita missão | JWT |
| GET | `/kapipass/rankings` | Ranking de jogadores | Não |
| GET | `/kapipass/diario` | Entradas do diário | JWT |
| POST | `/kapipass/diario` | Nova entrada no diário | JWT |
| GET | `/kapipass/tesouros` | Caça ao tesouro | JWT |
| GET | `/kapipass/eco` | EcoPass | JWT |

Swagger interativo (por serviço, dentro do container): acesse o serviço diretamente na rede Docker ou use `docker exec` — o gateway não expõe `/docs` centralizado.

---

## Autenticação (JWT)

### Fluxo compatível com o app mobile

1. **Registro ou login** retorna `{ access_token, token_type, refresh_token?, user }` — o app React Native continua usando apenas `access_token`
2. O app armazena o token e envia em requisições protegidas:

```http
Authorization: Bearer <access_token>
```

### Tokens

| Token | Validade padrão | Uso |
|-------|-----------------|-----|
| **Access** | 30 min (`JWT_ACCESS_EXPIRE_MINUTES`) | API requests |
| **Refresh** | 7 dias (`JWT_REFRESH_EXPIRE_DAYS`) | Renovar access token |

### Endpoints de autenticação

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Cadastro (retorna tokens + user) |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/refresh` | Renovar tokens (rotação de refresh) |
| POST | `/api/auth/logout` | Invalidar tokens (blacklist Redis) |
| GET | `/api/auth/me` | Perfil autenticado |
| POST | `/api/auth/change-password` | Alterar senha (autenticado) |
| POST | `/api/auth/forgot-password` | Solicitar recuperação por e-mail |
| POST | `/api/auth/reset-password` | Redefinir senha com token |
| GET | `/api/auth/verify-email?token=` | Confirmar e-mail |

### RBAC (Roles)

| Role | tipo_usuario_id | Permissões principais |
|------|-----------------|----------------------|
| ADMIN | 1 | Gestão completa |
| EMPRESA | 2 | Cupons, campanhas, relatórios |
| TURISTA | 3 | Favoritos, KapiPass, resgate de cupons |
| GUIA | 4 | Conteúdo, rotas |

O JWT inclui claim `role` derivado de `tipo_usuario_id`.

### Segurança

- Hash **Argon2** para novas senhas; **bcrypt** legado migrado automaticamente no login
- Blacklist de tokens via **Redis** no logout
- Rate limit reforçado em login (5/min) e cadastro (3/min)
- PATCH `/api/usuarios/{auth_id}` exige que o token corresponda ao `auth_id`

4. Rotas **internas** (`/api/internal/*`) exigem header:

```http
X-Internal-Key: <INTERNAL_SERVICE_KEY>
```

### Variáveis de ambiente (autenticação)

```env
JWT_SECRET=altere-em-producao
JWT_ACCESS_EXPIRE_MINUTES=30
JWT_REFRESH_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
REDIS_ENABLED=true
```

### Segurança por escopo (Etapa 2)

Rotas que aceitam `usuario_id` agora **exigem JWT** e validam que o id corresponde ao token:

| Serviço | Rotas protegidas |
|---------|------------------|
| **engagement** | favoritos, avaliações (com `usuario_id`) |
| **kapipass** | listagens com `usuario_id` (checkins, carimbos, etc.) |
| **commerce** | cupons resgatados, verificar, resgatar |

**Exceção EMPRESA:** parceiros podem consultar/resgatar cupons para turistas via QR (`LeitorQR`), quando `parceiro_id` coincide com o token.

O app mobile continua enviando `usuario_id` + Bearer — compatível sem alteração nas telas.

### Cache Redis (Etapa 2)

| Serviço | Dados em cache |
|---------|----------------|
| **content** | categorias, pontos, rotas |
| **engagement** | favoritos, média de avaliações |
| **commerce** | produtos, cupons disponíveis, resgatados |
| **kapipass** | níveis, rankings, progresso por usuário |

Invalidação automática nas operações de escrita.

### Frontend — refresh token e logout (Etapa 2)

- `lib/api/cliente-http.js`: persiste `refresh_token`, renova access token automaticamente em 401
- `lib/api/autenticacao.js`: login/register salvam ambos os tokens; logout chama `POST /auth/logout`

### PostgreSQL e Alembic (Etapa 3)

Por padrão o projeto continua usando **SQLite** (compatível com desenvolvimento local e testes). Para PostgreSQL:

```bash
docker compose --profile postgres up -d postgres
```

| Variável | Descrição |
|----------|-----------|
| `DATABASE_URL` | URL SQLAlchemy por serviço (ex.: `postgresql+psycopg2://kapitour:kapitour@localhost:5432/kapitour_auth`) |
| `USAR_ALEMBIC` | `true` aplica migrações versionadas em vez de `create_all` |
| `POSTGRES_PASSWORD` | Senha do container Postgres |

O script `backend/database/postgres/init-databases.sh` cria os bancos `kapitour_auth`, `kapitour_content`, `kapitour_engagement`, `kapitour_commerce` e `kapitour_kapipass`.

**Alembic:** migração inicial em cada serviço (`backend/services/{servico}/alembic/`). Runner compartilhado em `kapitour_shared/database/migracoes.py`.

### SMTP e e-mail assíncrono (Etapa 3)

| Variável | Descrição |
|----------|-----------|
| `SMTP_HOST` | Servidor SMTP (vazio = modo dev, apenas log) |
| `SMTP_PORT` | Porta (padrão 587) |
| `SMTP_USER` / `SMTP_PASSWORD` | Credenciais |
| `EMAIL_FROM` | Remetente |

Recuperação de senha e confirmação de e-mail usam `ServicoEmail` + fila Celery (`kapitour.enviar_email`).

### Cobertura de testes (Etapa 3)

```bash
cd backend
python scripts/run_tests.py all
python scripts/run_tests.py shared --cov
```

Meta de cobertura: **70%** nos módulos core de `kapitour_shared` (security, cache, email, workers, autenticação).

### Paginação e Swagger (Etapa 4)

Listagens de **pontos turísticos** e **rotas** aceitam parâmetros opcionais:

| Parâmetro | Descrição |
|-----------|-----------|
| `pagina` | Número da página (≥ 1) |
| `tamanho` | Itens por página (1–100) |

Sem `pagina`/`tamanho`, a API retorna a **lista completa** (compatível com o app React Native). Com paginação, retorna `{ itens, pagina, tamanho, total, total_paginas }`.

Helper compartilhado: `kapitour_shared/core/paginacao.py`.

Swagger (`/docs`) inclui tags, summaries, exemplos de modelos e códigos HTTP nas rotas de auth e content.

### Alembic em todos os serviços + Swagger ampliado (Etapa 5)

Migrações versionadas Alembic em **todos** os microserviços:

| Serviço | Pasta Alembic |
|---------|---------------|
| auth | `backend/services/auth/alembic/` |
| content | `backend/services/content/alembic/` |
| commerce | `backend/services/commerce/alembic/` |
| engagement | `backend/services/engagement/alembic/` |
| kapipass | `backend/services/kapipass/alembic/` |

Com PostgreSQL (`--profile postgres`), defina no `.env` as URLs por serviço e `USAR_ALEMBIC=true`:

```bash
AUTH_DATABASE_URL=postgresql+psycopg2://kapitour:kapitour@postgres:5432/kapitour_auth
CONTENT_DATABASE_URL=postgresql+psycopg2://kapitour:kapitour@postgres:5432/kapitour_content
# ... engagement, commerce, kapipass
USAR_ALEMBIC=true
docker compose --profile postgres up -d
```

**Paginação ampliada:** `GET /produtos` e `GET /cupons/disponiveis` aceitam `pagina`/`tamanho` opcionais (sem parâmetros = resposta atual, compatível com o app). Rankings KapiPass aceitam `pagina`/`tamanho` além de `page`/`size`.

**Swagger:** documentação enriquecida em commerce, engagement e kapipass (`/docs` em cada serviço ou via gateway).

### CI/CD, smoke tests e rate limiting (Etapa 6)

**GitHub Actions** (`.github/workflows/ci.yml`):

| Job | O que valida |
|-----|----------------|
| `backend-tests` | pytest em todos os microserviços + cobertura ≥ 70% em `kapitour_shared` |
| `frontend-tests` | Jest (app React Native) |
| `docker-build` | build das imagens monolito, microserviços e worker |
| `smoke-api` | sobe Redis + microserviços + gateway e executa rotas públicas |

Smoke local (com stack Docker rodando na porta 8080):

```bash
python backend/scripts/smoke_api.py --base-url http://localhost:8080
```

**Rate limiting** (Redis) em rotas sensíveis:

| Rota | Variável | Padrão |
|------|----------|--------|
| `POST /auth/login` | `RATE_LIMIT_LOGIN` | 5/min |
| `POST /auth/register` | `RATE_LIMIT_REGISTER` | 3/min |
| `POST /auth/forgot-password` | `RATE_LIMIT_FORGOT_PASSWORD` | 3/min |
| `POST /auth/refresh` | `RATE_LIMIT_REFRESH` | 10/min |
| `POST /kapipass/checkin` | `RATE_LIMIT_CHECKIN` | 30/min |
| `POST /cupons/resgatar` | `RATE_LIMIT_RESGATE_CUPOM` | 10/min |

Demais rotas usam `RATE_LIMIT_DEFAULT` (100/min por IP e por usuário autenticado).

**Observabilidade:** cada serviço expõe `GET /api/health`, `GET /api/status` e `GET /api/metrics` (Prometheus).

### Escopo JWT sem `usuario_id` (Etapa 7)

O app mobile deixou de enviar `usuario_id` na maioria das rotas user-scoped. O backend deriva o usuário do **Bearer JWT** via `resolver_usuario_escopo()`.

| Antes (legado) | Agora (preferido) |
|----------------|-------------------|
| `GET /favoritos?usuario_id=10` | `GET /favoritos` |
| `GET /cupons/resgatados/10` | `GET /cupons/resgatados/me` |
| `GET /kapipass/checkins?usuario_id=10` | `GET /kapipass/checkins` |
| Body `{ usuario_id, ponto_id }` | Body `{ ponto_id }` + JWT |

Rotas legadas com `usuario_id` continuam funcionando (compatibilidade). **Empresa (QR)** ainda envia `usuario_id` do turista escaneado em verificar/resgatar cupom.

---

## Banco de dados

### Arquivos por microserviço

| Arquivo | Serviço | Principais tabelas |
|---------|---------|-------------------|
| `auth.db` | auth | `usuarios` |
| `content.db` | content | `categorias`, `pontos_turisticos`, `ponto_categoria`, `rotas`, `rota_ponto` |
| `engagement.db` | engagement | `favoritos`, `avaliacoes`, `ponto_avaliacoes` |
| `commerce.db` | commerce | `produtos`, `tipos_produto`, `estoque`, `campanhas`, `cupons`, `cupons_resgatados` |
| `kapipass.db` | kapipass | `usuario_xp`, `kapipass_niveis`, check-ins, carimbos, missões, conquistas, etc. |

### Migrações e seed

Ao iniciar cada microserviço:

1. `Base.metadata.create_all` cria tabelas ausentes
2. `semear_dados_iniciais()` insere dados de demonstração se o banco estiver vazio (inclui pontos e rotas de Maricá no **content**)

### Consultar SQLite

```bash
# Windows / Linux / macOS
sqlite3 database/content.db

.tables
.schema pontos_turisticos
SELECT id, nome FROM pontos_turisticos LIMIT 5;
.quit
```

Via Docker (exemplo no content):

```bash
docker exec -it kapitour-content sqlite3 /app/database/content.db
```

---

## Testes (TDD / BDD)

O projeto adota **Test-Driven Development** e **Behavior-Driven Development** com cenários em português (**Dado / Quando / Então**).

### Backend — pytest + pytest-bdd

Cada microserviço possui sua própria pasta de testes:

```
backend/services/{servico}/tests/
├── features/*.feature      # Cenários Gherkin (# language: pt)
├── fakes/                  # Repositórios e clients fake
├── test_bdd_*.py           # Step definitions
└── test_*.py               # Testes unitários de domínio
```

**Instalar dependências de teste:**

```bash
cd backend
pip install -r requirements-dev.txt
```

**Executar todos os microserviços** (processo isolado por serviço):

```bash
python scripts/run_tests.py all
```

**Executar um microserviço:**

```bash
python scripts/run_tests.py auth
python scripts/run_tests.py commerce
python -m pytest services/kapipass/tests -v
```

| Microserviço | Cenários BDD | Testes unitários | Total |
|--------------|--------------|------------------|-------|
| auth | 6 | 4 | 10 |
| content | 3 | 3 | 6 |
| commerce | 4 | 3 | 7 |
| engagement | 3 | 3 | 6 |
| kapipass | 4 | 5 | 9 |

**Exemplo de cenário BDD** (`auth`):

```gherkin
Cenário: Login com credenciais válidas
  Dado que existe um usuário com email "turista@marica.gov.br" e senha "marica2024"
  Quando o usuário faz login com essas credenciais
  Então a autenticação é bem-sucedida
  E um token de acesso é emitido
```

### Frontend — Jest

Testes dos casos de uso em `lib/aplicacao/`:

```bash
npm install --legacy-peer-deps
npm test
npm run test:watch   # modo watch
```

Arquivo principal: `__tests__/lib/aplicacao/casos-de-uso/autenticacao.test.js`

---

## Usuários de demonstração

Inseridos automaticamente no seed do serviço **auth**:

| E-mail | Senha | Tipo (`tipo_usuario_id`) |
|--------|-------|--------------------------|
| admin@kapitour.com | admin123 | Administrador (1) |
| parceiro@kapitour.com | parceiro123 | Parceiro (2) |
| user@kapitour.com | user123 | Usuário comum (3) |

---

## Testes manuais com cURL

```bash
# Health do gateway
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@kapitour.com\",\"password\":\"user123\"}"

# Salve o token retornado e use nas próximas chamadas:
# export TOKEN="eyJ..."

# Perfil autenticado
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"

# Categorias e pontos
curl http://localhost:8000/api/categorias
curl http://localhost:8000/api/pontos-turisticos
curl http://localhost:8000/api/rotas

# Favoritos (autenticado)
curl http://localhost:8000/api/favoritos \
  -H "Authorization: Bearer $TOKEN"

# Cupons disponíveis
curl http://localhost:8000/api/cupons/disponiveis

# KapiPass — perfil gamificado
curl http://localhost:8000/api/kapipass/me \
  -H "Authorization: Bearer $TOKEN"
```

---

## Solução de problemas

| Problema | Possível causa | Solução |
|----------|----------------|---------|
| App não conecta à API | URL errada no `.env` | Use `10.0.2.2` no Android emulator ou IP da máquina no dispositivo físico |
| `Connection refused` na porta 8000 | Docker não está rodando | `docker compose up --build` |
| Banco vazio / sem pontos | Seed não executou | Apague `database/*.db` e suba os containers novamente |
| `401 Unauthorized` | Token expirado ou ausente | Faça login novamente |
| Testes backend falham com `No module named app.dominio` | Conflito com monolito `backend/app` | Use `python scripts/run_tests.py <servico>` (execução isolada) |
| `npm test` falha por peer deps | Conflito React 19 | `npm install --legacy-peer-deps` |

**Logs dos containers:**

```bash
docker compose logs -f gateway
docker compose logs -f auth
docker compose logs -f content
```

---

## Migração Supabase → SQLite

Esta versão **não utiliza Supabase**:

| Antes (Supabase) | Agora |
|------------------|-------|
| Supabase Auth | JWT próprio (email/senha) |
| PostgreSQL remoto | SQLite local por microserviço |
| OAuth Google via Supabase | Removido |
| Dados em produção Supabase | **Não migrados automaticamente** |

Para trazer dados históricos, exporte manualmente do Supabase e importe nos `.db` correspondentes ou recrie via seed/scripts.

---

## Licença

[0BSD](LICENSE) — uso livre com mínimas restrições.

---

## Repositório

https://github.com/LuanaPZenha/app_kapitour_test
