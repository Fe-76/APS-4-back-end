# APS 4 — Autenticação e Segurança em uma API RESTful

## 1. Descrição do Projeto
Esta aplicação é uma evolução da API RESTful de gestão de eventos acadêmicos desenvolvida na APS 2 e na APS 3.

Na APS 3 a API passou a usar **SQLite** e **SQLAlchemy ORM** para persistir eventos, participantes e inscrições, além de oferecer **relatórios consolidados**. Tudo isso continua funcionando.

Nesta versão (APS 4) foram adicionados mecanismos de **segurança**:
- Cadastro de **usuários** com senha armazenada como **hash Argon2** (biblioteca `pwdlib`);
- **Login** por e-mail e senha, retornando um **token JWT** (biblioteca `PyJWT`);
- **Proteção das rotas**: o token deve ser enviado no cabeçalho `Authorization: Bearer <token>`;
- **Controle de acesso por perfil** (`administrador` e `usuario`);
- Rota `/auth/me` para consultar os dados do usuário autenticado.

A arquitetura continua no padrão **MVC** com as camadas `Controller`, `Service`, `Model`, `Schema`, `Database` e agora `Security`.

---

## 2. Tecnologias Utilizadas
- **Linguagem:** Python 3.10+
- **Framework Web:** FastAPI
- **Servidor ASGI:** Uvicorn
- **ORM:** SQLAlchemy
- **Banco de Dados:** SQLite (arquivo `aps4.db`)
- **Validação de Dados:** Pydantic (v2) / `email-validator`
- **Hash de senhas:** `pwdlib[argon2]` (algoritmo Argon2)
- **Tokens JWT:** `PyJWT` (algoritmo HS256)
- **Documentação Interativa:** Swagger UI / ReDoc (integrados ao FastAPI)

---

## 3. Estrutura do Projeto

```text
APS_Parte4/
├── main.py                  # Ponto de entrada, criação das tabelas e do administrador inicial
├── database.py              # Configuração da conexão SQLite, SessionLocal e Base do SQLAlchemy
├── requirements.txt         # Dependências do projeto
├── README.md                # Documentação da aplicação
├── controller/              # Camada Controller (Rotas HTTP)
│   ├── evento_controller.py
│   ├── participante_controller.py
│   ├── inscricao_controller.py
│   ├── relatorio_controller.py
│   ├── usuario_controller.py    # NOVO
│   └── auth_controller.py       # NOVO
├── model/                   # Camada Model (Tabelas SQLAlchemy)
│   ├── evento.py
│   ├── participante.py
│   ├── inscricao.py
│   └── usuario.py               # NOVO
├── schema/                  # Camada Schema (Validação Pydantic)
│   ├── evento_schema.py
│   ├── participante_schema.py
│   ├── inscricao_schema.py
│   ├── relatorio_schema.py
│   ├── usuario_schema.py        # NOVO
│   └── auth_schema.py           # NOVO
├── service/                 # Camada Service (Regras de Negócio)
│   ├── evento_service.py
│   ├── participante_service.py
│   ├── inscricao_service.py
│   ├── relatorio_service.py
│   ├── usuario_service.py       # NOVO
│   └── auth_service.py          # NOVO
└── security/                # NOVO: Camada de Segurança
    └── security.py          # Hash de senha, geração/validação de JWT e dependências de acesso
```

- **security.py**: `gerar_hash_senha`, `verificar_senha`, `criar_token`, `ler_token` e as dependências `get_usuario_atual` (exige token válido) e `verificar_admin` (exige perfil administrador). As rotas só usam `Depends(...)`, então a lógica de autenticação não fica repetida nos controllers.

---

## 4. Configuração do Banco de Dados
A conexão é gerenciada no arquivo `database.py`:
- **Engine:** `create_engine("sqlite:///./aps4.db", connect_args={"check_same_thread": False})`
- **Sessão:** `get_db()` abre uma sessão por requisição e fecha no `finally`.
- **Tabelas:** `Base.metadata.create_all(bind=engine)` é chamado no `main.py` e cria `eventos`, `participantes`, `inscricoes` e `usuarios`.
- **Arquivo do Banco:** `aps4.db`, gerado na raiz do projeto (ignorado pelo Git).

### Tabela `usuarios`
| Coluna | Descrição |
|---|---|
| `id` | identificador único |
| `nome` | nome do usuário |
| `email` | e-mail de login (único) |
| `senha_hash` | hash Argon2 da senha (a senha original **não** é salva) |
| `perfil` | `administrador` ou `usuario` |

---

## 5. Configuração da Chave Secreta e do Administrador

A chave usada para assinar os tokens **não fica no código**. Ela é lida da variável de ambiente `SECRET_KEY`.

| Variável | Obrigatória | Descrição |
|---|---|---|
| `SECRET_KEY` | Recomendada | Chave para assinar os tokens JWT. Se não for definida, a API gera uma chave temporária a cada execução (os tokens deixam de valer ao reiniciar). |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Não | Validade do token em minutos (padrão: `30`). |
| `ADMIN_EMAIL` | Não | E-mail do administrador inicial. |
| `ADMIN_SENHA` | Não | Senha do administrador inicial. |
| `ADMIN_NOME` | Não | Nome do administrador inicial (padrão: `Administrador`). |

Para gerar uma chave aleatória:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Criação do administrador inicial
O cadastro público (`POST /usuarios`) **sempre** cria usuários com perfil `usuario`. Mesmo que alguém envie `"perfil": "administrador"` no corpo, o campo é ignorado.

O primeiro administrador é criado de forma controlada: ao iniciar, se `ADMIN_EMAIL` e `ADMIN_SENHA` estiverem definidas e esse e-mail ainda não existir, a API cria esse usuário com perfil `administrador`.

Depois disso, um administrador pode promover outros usuários com `PUT /usuarios/{id}/perfil`.

---

## 6. Instruções de Instalação e Execução

### Passo 1: Entrar na pasta do projeto
```bash
cd APS_Parte4
```

### Passo 2: Criar e Ativar Ambiente Virtual (Recomendado)
- **Windows:**
  ```cmd
  python -m venv venv
  venv\Scripts\activate
  ```
- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### Passo 3: Instalar as Dependências
```bash
pip install -r requirements.txt
```

### Passo 4: Definir as Variáveis de Ambiente
- **Windows (PowerShell):**
  ```powershell
  $env:SECRET_KEY="cole-aqui-a-chave-gerada"
  $env:ADMIN_EMAIL="admin@aps.com"
  $env:ADMIN_SENHA="admin123"
  ```
- **Windows (CMD):**
  ```cmd
  set SECRET_KEY=cole-aqui-a-chave-gerada
  set ADMIN_EMAIL=admin@aps.com
  set ADMIN_SENHA=admin123
  ```
- **Linux / macOS:**
  ```bash
  export SECRET_KEY="cole-aqui-a-chave-gerada"
  export ADMIN_EMAIL="admin@aps.com"
  export ADMIN_SENHA="admin123"
  ```

### Passo 5: Executar a API
```bash
uvicorn main:app --reload
```
A API estará acessível em: `http://127.0.0.1:8000`

---

## 7. Documentação Interativa (Swagger)
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Como usar o token no Swagger
1. Faça login em `POST /auth/login` e copie o valor de `access_token`;
2. Clique no botão **Authorize** (cadeado) no topo da página;
3. Cole o token no campo e clique em **Authorize**;
4. A partir daí o Swagger envia `Authorization: Bearer <token>` em todas as requisições.

---

## 8. Perfis e Permissões

| Rota | Público | Usuário | Administrador |
|---|:---:|:---:|:---:|
| `GET /` | ✅ | ✅ | ✅ |
| `POST /usuarios` (cadastro) | ✅ | ✅ | ✅ |
| `POST /auth/login` | ✅ | ✅ | ✅ |
| `GET /auth/me` | ❌ | ✅ | ✅ |
| `GET /usuarios` | ❌ | ❌ | ✅ |
| `PUT /usuarios/{id}/perfil` | ❌ | ❌ | ✅ |
| `GET /eventos`, `GET /eventos/{id}` | ❌ | ✅ | ✅ |
| `POST /eventos` | ❌ | ❌ | ✅ |
| `PUT /eventos/{id}` | ❌ | ❌ | ✅ |
| `DELETE /eventos/{id}` | ❌ | ❌ | ✅ |
| `GET /participantes`, `GET /participantes/{id}` | ❌ | ✅ | ✅ |
| `POST /participantes` | ❌ | ✅ | ✅ |
| `PUT /participantes/{id}` | ❌ | ❌ | ✅ |
| `DELETE /participantes/{id}` | ❌ | ❌ | ✅ |
| `POST /eventos/{evento_id}/inscricoes/{participante_id}` | ❌ | ✅ | ✅ |
| `GET /eventos/{evento_id}/inscricoes` | ❌ | ✅ | ✅ |
| `GET /relatorios/...` (os três relatórios) | ❌ | ❌ | ✅ |

- **Público:** sem token. Rotas marcadas com ❌ retornam **401**.
- **Usuário:** consulta eventos e participantes, cadastra participantes, faz inscrições e vê seus próprios dados (`/auth/me`). Ao tentar uma operação de administrador recebe **403**.
- **Administrador:** acesso total, incluindo gerenciar eventos, editar/excluir participantes, ver relatórios e promover usuários.

A permissão é verificada **no servidor**: o perfil é lido do banco a partir do `id` gravado no token, nunca de um campo enviado pelo cliente.

---

## 9. Rotas da API e Exemplos de Uso

### 9.1. Usuários e Autenticação

**Cadastrar usuário — `POST /usuarios`**
```json
{
  "nome": "Aluno Exemplo",
  "email": "aluno@exemplo.com",
  "senha": "senha_segura"
}
```
Resposta (**201**) — sem senha e sem hash:
```json
{
  "id": 2,
  "nome": "Aluno Exemplo",
  "email": "aluno@exemplo.com",
  "perfil": "usuario"
}
```
Validações: nome não vazio, e-mail válido, senha com no mínimo 6 caracteres (**422**) e e-mail único (**409**).

**Login — `POST /auth/login`**
```json
{
  "email": "aluno@exemplo.com",
  "senha": "senha_segura"
}
```
Resposta (**200**):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```
O token contém `sub` (id do usuário) e `exp` (data de expiração). É assinado com HS256 usando a `SECRET_KEY`.

**Dados do usuário logado — `GET /auth/me`** (com token)
```json
{
  "id": 2,
  "nome": "Aluno Exemplo",
  "email": "aluno@exemplo.com",
  "perfil": "usuario"
}
```

**Promover usuário — `PUT /usuarios/{id}/perfil`** (somente administrador)
```json
{
  "perfil": "administrador"
}
```

### 9.2. Eventos (`/eventos`)
- `POST /eventos` — Cadastrar evento (administrador)
- `GET /eventos` — Listar eventos (autenticado)
- `GET /eventos/{id}` — Buscar evento (autenticado)
- `PUT /eventos/{id}` — Atualizar evento (administrador)
- `DELETE /eventos/{id}` — Excluir evento e suas inscrições (administrador)

```json
{
  "titulo": "Introdução à Inteligência Artificial",
  "descricao": "Palestra sobre o impacto do Machine Learning na indústria.",
  "data": "2026-11-25",
  "horario": "19:00",
  "local": "Auditório Principal",
  "capacidade": 100,
  "categoria": "Palestra"
}
```

### 9.3. Participantes (`/participantes`)
- `POST /participantes` — Cadastrar participante (autenticado)
- `GET /participantes` — Listar participantes (autenticado)
- `GET /participantes/{id}` — Buscar participante (autenticado)
- `PUT /participantes/{id}` — Atualizar participante (administrador)
- `DELETE /participantes/{id}` — Excluir participante e suas inscrições (administrador)

```json
{
  "nome": "Nicolas Vieira Marques",
  "email": "nicolas.marques@aluno.unisenai.edu.br",
  "curso": "Engenharia de Software"
}
```

### 9.4. Inscrições
- `POST /eventos/{evento_id}/inscricoes/{participante_id}` — Realizar inscrição (autenticado)
  - Evento inexistente → **404**; participante inexistente → **404**;
  - Inscrição duplicada → **409**; sem vagas → **409**.
- `GET /eventos/{evento_id}/inscricoes` — Listar inscritos (autenticado)

### 9.5. Relatórios (`/relatorios`) — somente administrador
- `GET /relatorios/eventos/ocupacao` — capacidade, inscritos, vagas e percentual de ocupação de cada evento;
- `GET /relatorios/eventos/categorias` — total de eventos, capacidade e inscrições por categoria;
- `GET /relatorios/participantes/cursos` — total de participantes (sem duplicidade) e de inscrições por curso.

```json
[
  {
    "evento_id": 1,
    "titulo": "Introdução à Inteligência Artificial",
    "capacidade": 100,
    "total_inscritos": 75,
    "vagas_disponiveis": 25,
    "percentual_ocupacao": 75.0
  }
]
```

---

## 10. Tratamento de Erros

| Situação | Código | Mensagem |
|---|---|---|
| E-mail ou senha incorretos no login | 401 | `"E-mail ou senha inválidos."` |
| Token ausente, inválido, adulterado ou expirado | 401 | `"Não foi possível validar as credenciais."` |
| Usuário sem permissão | 403 | `"Você não possui permissão para executar esta operação."` |
| E-mail de usuário já cadastrado | 409 | `"Já existe um usuário cadastrado com este e-mail."` |
| Evento / participante / usuário inexistente | 404 | `"Evento não encontrado."` etc. |
| Inscrição duplicada / sem vagas | 409 | mensagens da APS 3 |
| Dados inválidos (Pydantic) | 422 | detalhes da validação |

A mensagem de login é a mesma para e-mail inexistente e senha errada, para não revelar qual dos dois está incorreto.

---

## 11. Guia de Testes (Seção 13 do enunciado)

Inicie a API com `SECRET_KEY`, `ADMIN_EMAIL=admin@aps.com` e `ADMIN_SENHA=admin123` definidas e acesse `/docs`.

1. **Cadastro de usuário:** `POST /usuarios` com `{"nome": "Aluno", "email": "aluno@ex.com", "senha": "senha123", "perfil": "administrador"}` → **201** com `"perfil": "usuario"` (o perfil enviado foi ignorado).
2. **Senha armazenada como hash:** abra o arquivo `aps4.db` (ex.: DB Browser for SQLite) e veja a coluna `senha_hash` da tabela `usuarios`, com valores como `$argon2id$v=19$m=65536,t=3,p=4$...`. A senha original não aparece.
3. **E-mail duplicado:** repita o cadastro → **409**.
4. **Login válido:** `POST /auth/login` com `aluno@ex.com` / `senha123` → **200** com `access_token`.
5. **Login inválido:** senha errada ou e-mail inexistente → **401** `"E-mail ou senha inválidos."`.
6. **Rota protegida sem token:** sem clicar em Authorize, `GET /eventos` → **401**.
7. **Rota protegida com token válido:** clique em Authorize, cole o token do aluno, `GET /eventos` → **200**.
8. **Token inválido ou expirado:** em Authorize cole um token alterado (ex.: troque a última letra) → **401**. Para testar a expiração, inicie a API com `ACCESS_TOKEN_EXPIRE_MINUTES=1`, faça login, espere 1 minuto e repita a requisição → **401**.
9. **Operação de administrador por usuário comum:** com o token do aluno, `POST /eventos` ou `GET /relatorios/eventos/ocupacao` → **403**.
10. **Operação de administrador por administrador:** faça login com `admin@aps.com` / `admin123`, use esse token e faça `POST /eventos` → **201**.
11. **`/auth/me`:** com cada token, `GET /auth/me` retorna os dados do dono do token (sem senha e sem hash).
12. **Funcionalidades da APS 3:** com token, cadastre participantes, faça inscrições (teste duplicada → 409 e sem vagas → 409) e, com o token de administrador, consulte os três relatórios. Reinicie o Uvicorn e verifique que os dados continuam no `aps4.db`.
