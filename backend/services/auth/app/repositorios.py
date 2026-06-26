"""Compatibilidade — reexporta adaptador de persistência."""

from app.infraestrutura.persistencia.repositorio_usuario import RepositorioUsuarioSqlAlchemy as RepositorioUsuario

__all__ = ["RepositorioUsuario"]
