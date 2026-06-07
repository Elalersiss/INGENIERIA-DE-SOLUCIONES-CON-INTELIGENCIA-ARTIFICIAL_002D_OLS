-- ============================================================
-- Schema para el Chatbot Telegram con LangGraph y Supabase
-- Clase 3.5 - Ingeniería de Soluciones con IA - DuocUC
-- ============================================================

-- Migracion: agregar step_order si la tabla traces ya existe
alter table if exists traces add column if not exists step_order int not null default 0;


-- Sesiones: una por usuario de Telegram
create table if not exists sessions (
  id               uuid        primary key default gen_random_uuid(),
  telegram_chat_id bigint      not null,
  thread_id        text        not null,
  created_at       timestamptz default now()
);

-- Mensajes: cada mensaje enviado o recibido
create table if not exists messages (
  id         uuid        primary key default gen_random_uuid(),
  session_id uuid        not null references sessions(id) on delete cascade,
  role       text        not null check (role in ('user', 'assistant')),
  content    text        not null,
  blocked    boolean     default false,
  created_at timestamptz default now()
);

-- Trazas: cada nodo del grafo LangGraph ejecutado
create table if not exists traces (
  id          uuid        primary key default gen_random_uuid(),
  session_id  uuid        not null references sessions(id) on delete cascade,
  message_id  uuid        not null references messages(id) on delete cascade,
  step_order  int         not null,
  node_name   text        not null,
  tool_name   text,
  started_at  timestamptz not null,
  ended_at    timestamptz not null,
  duration_ms int         not null,
  input       jsonb,
  output      jsonb,
  created_at  timestamptz default now()
);
