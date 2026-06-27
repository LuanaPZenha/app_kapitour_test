"""Testes unitários da infraestrutura compartilhada."""

import pytest

from kapitour_shared.security.passwords import gerar_hash_senha, precisa_rehash, senha_confere
from kapitour_shared.security.rbac import Role, possui_permissao, role_de_tipo_usuario
from kapitour_shared.autenticacao import (
    UsuarioToken,
    resolver_usuario_escopo,
    validar_consulta_cupom_usuario,
    validar_resgate_cupom,
)
from fastapi import HTTPException
import pytest


class TestPasswords:
    def test_argon2_hash_e_verificacao(self):
        hash_senha = gerar_hash_senha("MinhaSenh@123")
        assert senha_confere("MinhaSenh@123", hash_senha)
        assert not senha_confere("errada", hash_senha)
        assert not precisa_rehash(hash_senha)

    def test_bcrypt_legado(self):
        import bcrypt

        hash_bcrypt = bcrypt.hashpw(b"legado123", bcrypt.gensalt()).decode()
        assert senha_confere("legado123", hash_bcrypt)
        assert precisa_rehash(hash_bcrypt)


class TestRBAC:
    def test_role_de_tipo_usuario(self):
        assert role_de_tipo_usuario(1) == Role.ADMIN
        assert role_de_tipo_usuario(3) == Role.TURISTA

    def test_permissoes_admin(self):
        assert possui_permissao(Role.ADMIN, "usuarios:deletar")

    def test_turista_sem_permissao_admin(self):
        assert not possui_permissao(Role.TURISTA, "usuarios:deletar")

    def test_turista_pode_resgatar_cupom(self):
        assert possui_permissao(Role.TURISTA, "cupons:resgatar")


class TestEscopoUsuario:
    def test_resolver_usuario_escopo_aceita_proprio_id(self):
        usuario = UsuarioToken(id=10, auth_id="a", role=Role.TURISTA)
        assert resolver_usuario_escopo(usuario, 10) == 10

    def test_resolver_usuario_escopo_rejeita_id_diferente(self):
        usuario = UsuarioToken(id=10, auth_id="a", role=Role.TURISTA)
        with pytest.raises(HTTPException) as exc:
            resolver_usuario_escopo(usuario, 99)
        assert exc.value.status_code == 403

    def test_empresa_pode_consultar_cupom_de_turista(self):
        empresa = UsuarioToken(id=2, auth_id="e", role=Role.EMPRESA)
        validar_consulta_cupom_usuario(empresa, 99)

    def test_empresa_resgata_com_parceiro_correto(self):
        empresa = UsuarioToken(id=2, auth_id="e", role=Role.EMPRESA)
        validar_resgate_cupom(empresa, usuario_id=99, parceiro_id=2)
