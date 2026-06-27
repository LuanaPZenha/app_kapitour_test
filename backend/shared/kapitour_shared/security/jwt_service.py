from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt

from kapitour_shared.cache.redis_client import obter_cliente_redis
from kapitour_shared.configuracao import configuracoes
from kapitour_shared.security.rbac import Role, role_de_tipo_usuario


@dataclass(frozen=True)
class ParTokens:
    access_token: str
    refresh_token: str
    access_jti: str
    refresh_jti: str


class ServicoJWT:
    """Gerencia access/refresh tokens, blacklist e rotação via Redis."""

    PREFIXO_BLACKLIST = "jwt:blacklist:"
    PREFIXO_REFRESH = "jwt:refresh:"
    PREFIXO_SESSAO = "jwt:sessao:"

    def criar_par_tokens(
        self,
        auth_id: str,
        usuario_id: int,
        tipo_usuario_id: int = 3,
    ) -> ParTokens:
        role = role_de_tipo_usuario(tipo_usuario_id)
        access_jti = str(uuid4())
        refresh_jti = str(uuid4())

        access_exp = datetime.utcnow() + timedelta(minutes=configuracoes.jwt_access_expire_minutes)
        refresh_exp = datetime.utcnow() + timedelta(days=configuracoes.jwt_refresh_expire_days)

        access_payload = {
            "sub": auth_id,
            "user_id": usuario_id,
            "jti": access_jti,
            "type": "access",
            "role": role.value,
            "exp": access_exp,
        }
        refresh_payload = {
            "sub": auth_id,
            "user_id": usuario_id,
            "jti": refresh_jti,
            "type": "refresh",
            "role": role.value,
            "exp": refresh_exp,
        }

        access_token = jwt.encode(
            access_payload, configuracoes.jwt_secret, algorithm=configuracoes.jwt_algorithm
        )
        refresh_token = jwt.encode(
            refresh_payload, configuracoes.jwt_secret, algorithm=configuracoes.jwt_algorithm
        )

        self._registrar_refresh(refresh_jti, auth_id, refresh_exp)
        self._registrar_sessao(auth_id, refresh_jti)

        return ParTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
        )

    def decodificar(self, token: str) -> dict | None:
        try:
            payload = jwt.decode(
                token,
                configuracoes.jwt_secret,
                algorithms=[configuracoes.jwt_algorithm],
            )
        except JWTError:
            return None

        jti = payload.get("jti")
        if jti and self._esta_na_blacklist(jti):
            return None
        return payload

    def renovar_tokens(self, refresh_token: str) -> ParTokens | None:
        payload = self.decodificar(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        jti = payload.get("jti")
        auth_id = payload.get("sub")
        usuario_id = payload.get("user_id")
        if not jti or not auth_id or usuario_id is None:
            return None

        if not self._refresh_valido(jti):
            return None

        self.revogar_refresh(jti)
        tipo = self._tipo_usuario_de_role(payload.get("role", "TURISTA"))
        return self.criar_par_tokens(auth_id, int(usuario_id), tipo)

    def revogar_refresh(self, jti: str) -> None:
        redis = obter_cliente_redis()
        if not redis:
            return
        exp = redis.get(f"{self.PREFIXO_REFRESH}{jti}")
        if exp:
            ttl = max(int(float(exp) - datetime.utcnow().timestamp()), 1)
            redis.setex(f"{self.PREFIXO_BLACKLIST}{jti}", ttl, "1")
        redis.delete(f"{self.PREFIXO_REFRESH}{jti}")

    def revogar_todas_sessoes(self, auth_id: str) -> None:
        redis = obter_cliente_redis()
        if not redis:
            return
        chave = f"{self.PREFIXO_SESSAO}{auth_id}"
        jtis = redis.smembers(chave) or []
        for jti in jtis:
            self.revogar_refresh(jti)
        redis.delete(chave)

    def logout(self, access_token: str | None, refresh_token: str | None) -> None:
        for token in (access_token, refresh_token):
            if not token:
                continue
            payload = self.decodificar(token) or self._decodificar_sem_blacklist(token)
            if not payload:
                continue
            jti = payload.get("jti")
            exp = payload.get("exp")
            if jti and exp:
                ttl = max(int(exp - datetime.utcnow().timestamp()), 1)
                redis = obter_cliente_redis()
                if redis:
                    redis.setex(f"{self.PREFIXO_BLACKLIST}{jti}", ttl, "1")
            if payload.get("type") == "refresh" and jti:
                self.revogar_refresh(jti)

    def _decodificar_sem_blacklist(self, token: str) -> dict | None:
        try:
            return jwt.decode(
                token,
                configuracoes.jwt_secret,
                algorithms=[configuracoes.jwt_algorithm],
            )
        except JWTError:
            return None

    def _esta_na_blacklist(self, jti: str) -> bool:
        redis = obter_cliente_redis()
        if not redis:
            return False
        return bool(redis.exists(f"{self.PREFIXO_BLACKLIST}{jti}"))

    def _refresh_valido(self, jti: str) -> bool:
        redis = obter_cliente_redis()
        if not redis:
            return True
        return bool(redis.exists(f"{self.PREFIXO_REFRESH}{jti}"))

    def _registrar_refresh(self, jti: str, auth_id: str, expira: datetime) -> None:
        redis = obter_cliente_redis()
        if not redis:
            return
        ttl = max(int((expira - datetime.utcnow()).total_seconds()), 1)
        redis.setex(f"{self.PREFIXO_REFRESH}{jti}", ttl, auth_id)

    def _registrar_sessao(self, auth_id: str, refresh_jti: str) -> None:
        redis = obter_cliente_redis()
        if not redis:
            return
        chave = f"{self.PREFIXO_SESSAO}{auth_id}"
        redis.sadd(chave, refresh_jti)
        redis.expire(chave, configuracoes.jwt_refresh_expire_days * 86400)

    @staticmethod
    def _tipo_usuario_de_role(role: str) -> int:
        mapa = {"ADMIN": 1, "EMPRESA": 2, "TURISTA": 3, "GUIA": 4}
        return mapa.get(role, 3)


# Singleton
servico_jwt = ServicoJWT()


def criar_token_acesso(auth_id: str, usuario_id: int, tipo_usuario_id: int = 3) -> str:
    """Compatibilidade — retorna apenas access token."""
    return servico_jwt.criar_par_tokens(auth_id, usuario_id, tipo_usuario_id).access_token
