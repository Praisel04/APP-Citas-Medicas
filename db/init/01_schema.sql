\set ON_ERROR_STOP on

-- Extensión UUID
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- ===== Tipos =====
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'estado_cita') THEN
    CREATE TYPE estado_cita AS ENUM ('programada', 'cancelada', 'realizada');
  END IF;
END $$;

-- ===== TABLAS =====

-- USUARIO
CREATE TABLE IF NOT EXISTS usuario (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(100) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  rol VARCHAR(50),
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
  
);

-- CITA
CREATE TABLE IF NOT EXISTS cita (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id UUID NOT NULL REFERENCES usuario(id) ON DELETE CASCADE,
  nombre_cita VARCHAR(255) NOT NULL,
  fecha_hora TIMESTAMPTZ NOT NULL,
  estado estado_cita NOT NULL DEFAULT 'programada',
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- ===== ÍNDICES =====
CREATE INDEX IF NOT EXISTS ix_cita_usuario_fecha ON cita (usuario_id, fecha_hora);
CREATE INDEX IF NOT EXISTS ix_cita_estado ON cita (estado);

-- ===== TRIGGERS updated_at =====
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_usuario_updated_at') THEN
    CREATE TRIGGER trg_usuario_updated_at
    BEFORE UPDATE ON usuario
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_cita_updated_at') THEN
    CREATE TRIGGER trg_cita_updated_at
    BEFORE UPDATE ON cita
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;

-- ===== USUARIO DE APLICACIÓN =====
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'appuser') THEN
    CREATE ROLE appuser LOGIN PASSWORD 'supersecret_dev';
  END IF;
END $$;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO appuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO appuser;
