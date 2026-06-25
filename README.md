# Kapitour

Aplicativo mobile de turismo (React Native/Expo) com API backend em FastAPI e banco SQLite3.

## Arquitetura

```
appkapitour/
├── backend/           # API FastAPI + SQLAlchemy + SQLite
├── database/          # Arquivo kapitour.db (volume Docker persistente)
├── Screens/           # Telas do app mobile
├── components/        # Componentes React Native
├── lib/api.js         # Cliente HTTP (substitui Supabase)
├── docker-compose.yml
└── Dockerfile
```

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose
- Node.js 18+ (para o app mobile)
- Expo CLI (`npm install -g expo-cli`)

## Configuração

Copie ou edite o arquivo `.env` na raiz:

```env
DATABASE_URL=sqlite:///database/kapitour.db
JWT_SECRET=kapitour-dev-secret-change-in-production
CORS_ORIGINS=*
EXPO_PUBLIC_API_URL=http://localhost:8000/api
```

> **Emulador Android:** use `http://10.0.2.2:8000/api`  
> **Dispositivo físico:** use o IP da sua máquina, ex.: `http://192.168.1.10:8000/api`

## Executar com Docker (recomendado)

```bash
docker compose up --build
```

A API ficará disponível em:

- **API:** http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/api/health

O banco SQLite é persistido em `./database/kapitour.db` via volume Docker.

## Executar localmente (sem Docker)

### Backend

```bash
pip install -r backend/requirements.txt
set PYTHONPATH=backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### App mobile

```bash
npm install
npm start
```

## Acessar o banco SQLite

### Via linha de comando

```bash
sqlite3 database/kapitour.db
```

Comandos úteis:

```sql
.tables
.schema usuarios
SELECT id, nome, email, tipo_usuario_id FROM usuarios;
.quit
```

### Via Docker

```bash
docker exec -it kapitour sqlite3 /app/database/kapitour.db
```

## Usuários de demonstração (seed)

| Email | Senha | Tipo |
|-------|-------|------|
| admin@kapitour.com | admin123 | Administrador (1) |
| parceiro@kapitour.com | parceiro123 | Parceiro (2) |
| user@kapitour.com | user123 | Usuário comum (3) |

## Estrutura do banco de dados

| Tabela | Descrição |
|--------|-----------|
| `usuarios` | Usuários do sistema (auth_id, senha_hash, tipo_usuario_id) |
| `pontos_turisticos` | Lugares/pontos turísticos |
| `categorias` | Categorias de pontos |
| `ponto_categoria` | Relacionamento N:N pontos ↔ categorias |
| `rotas` | Rotas turísticas |
| `rota_ponto` | Pontos de uma rota (com ordem) |
| `favoritos` | Pontos favoritos por usuário |
| `avaliacoes` | Avaliações de pontos |
| `ponto_avaliacoes` | Avaliações durante rotas |
| `produtos` | Produtos da loja |
| `tipos_produto` | Tipos de produto |
| `estoque` | Estoque por produto |
| `campanhas` | Campanhas promocionais |
| `cupons` | Cupons de desconto |
| `cupons_resgatados` | Histórico de resgates |

### Migrações automáticas

Ao iniciar a API, o sistema:

1. Verifica se as tabelas existem (`Base.metadata.create_all`)
2. Cria automaticamente as tabelas ausentes
3. Insere dados de demonstração se o banco estiver vazio

## Endpoints principais da API

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/api/auth/register` | Cadastro |
| POST | `/api/auth/login` | Login (retorna JWT) |
| GET | `/api/auth/me` | Usuário autenticado |
| GET | `/api/categorias` | Listar categorias |
| GET | `/api/pontos-turisticos` | Listar pontos |
| GET | `/api/rotas` | Listar rotas |
| GET | `/api/favoritos` | Favoritos do usuário |
| POST | `/api/favoritos` | Adicionar favorito |
| DELETE | `/api/favoritos` | Remover favorito |
| GET | `/api/produtos` | Produtos da loja |
| GET | `/api/cupons/disponiveis` | Cupons disponíveis |
| POST | `/api/cupons/resgatar` | Resgatar cupom |

Documentação completa: http://localhost:8000/docs

## Testes manuais da API

```bash
# Health
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"user@kapitour.com\",\"password\":\"user123\"}"

# Listar categorias
curl http://localhost:8000/api/categorias

# Listar pontos
curl http://localhost:8000/api/pontos-turisticos

# Listar rotas
curl http://localhost:8000/api/rotas
```

## Migração Supabase → SQLite

Esta versão remove completamente o Supabase:

- Autenticação via JWT (email/senha)
- Persistência via API REST + SQLite3
- OAuth Google removido (dependia do Supabase Auth)
- Dados do Supabase em produção **não são migrados automaticamente**

## Licença

0BSD
