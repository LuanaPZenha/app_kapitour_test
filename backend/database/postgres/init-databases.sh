#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    SELECT 'CREATE DATABASE kapitour_auth' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kapitour_auth')\gexec
    SELECT 'CREATE DATABASE kapitour_content' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kapitour_content')\gexec
    SELECT 'CREATE DATABASE kapitour_engagement' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kapitour_engagement')\gexec
    SELECT 'CREATE DATABASE kapitour_commerce' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kapitour_commerce')\gexec
    SELECT 'CREATE DATABASE kapitour_kapipass' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'kapitour_kapipass')\gexec
EOSQL
