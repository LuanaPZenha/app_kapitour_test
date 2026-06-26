"""Compatibilidade — reexporta modelo ORM."""

from app.infraestrutura.persistencia.modelos import UsuarioModelo as Usuario

__all__ = ["Usuario"]
