from datetime import date, datetime

from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.models import Campanha, Categoria, Cupom, PontoTuristico, Rota, Usuario
from app.repositories import (
    CategoryRepository,
    CouponRepository,
    FavoriteRepository,
    PlaceRepository,
    RatingRepository,
    RouteRepository,
    StoreRepository,
    UserRepository,
)
from app.schemas import UsuarioResponse


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def register(self, nome, email, password, **kwargs) -> dict:
        if self.users.email_exists(email):
            raise ValueError("Este email já está cadastrado.")
        user = self.users.create(
            nome=nome,
            email=email,
            password=password,
            cpf=kwargs.get("cpf"),
            sexo=kwargs.get("sexo"),
            data_nascimento=kwargs.get("data_nascimento"),
            tipo_usuario_id=kwargs.get("tipo_usuario_id", 3),
        )
        token = create_access_token(user.auth_id, user.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(user),
        }

    def login(self, email: str, password: str) -> dict:
        user = self.users.authenticate(email, password)
        if not user:
            raise ValueError("Credenciais inválidas.")
        token = create_access_token(user.auth_id, user.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(user),
        }

    def google_login_or_register(self, id_token: str) -> dict:
        import json
        import os
        import urllib.request

        url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                info = json.loads(resp.read().decode())
        except Exception:
            raise ValueError("Token Google inválido ou expirado.")

        email = info.get("email")
        name = info.get("name") or (email.split("@")[0] if email else "Usuário")

        if not email:
            raise ValueError("Não foi possível obter o email da conta Google.")

        user = self.users.get_by_email(email)
        if not user:
            user = self.users.create(
                nome=name,
                email=email,
                password=os.urandom(32).hex(),
                tipo_usuario_id=3,
            )

        token = create_access_token(user.auth_id, user.id)
        return {
            "access_token": token,
            "user": UsuarioResponse.model_validate(user),
        }


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def get_by_auth_id(self, auth_id: str) -> Usuario | None:
        return self.users.get_by_auth_id(auth_id)

    def update(self, auth_id: str, data: dict) -> Usuario:
        user = self.users.get_by_auth_id(auth_id)
        if not user:
            raise ValueError("Usuário não encontrado.")
        if data.get("email") and self.users.get_by_email(data["email"]) and self.users.get_by_email(data["email"]).id != user.id:
            raise ValueError("Email já cadastrado.")
        return self.users.update(user, data)


class FavoriteService:
    def __init__(self, db: Session):
        self.favorites = FavoriteRepository(db)
        self.places = PlaceRepository(db)

    def list_with_places(self, usuario_id: int) -> list[dict]:
        favoritos = self.favorites.list_by_user(usuario_id)
        result = []
        for fav in favoritos:
            ponto = self.places.get_by_id(fav.ponto_id)
            ponto_data = None
            if ponto:
                ponto_data = {
                    "id": ponto.id,
                    "nome": ponto.nome,
                    "descricao": ponto.descricao,
                    "latitude": ponto.latitude,
                    "longitude": ponto.longitude,
                    "url_img": ponto.url_img,
                    "rua_numero": ponto.rua_numero,
                }
            result.append(
                {
                    "id": fav.id,
                    "usuario_id": fav.usuario_id,
                    "ponto_id": fav.ponto_id,
                    "data_adicionado": fav.data_adicionado.isoformat(),
                    "pontos_turisticos": ponto_data,
                }
            )
        return result


class CouponService:
    def __init__(self, db: Session):
        self.coupons = CouponRepository(db)
        self.users = UserRepository(db)

    def list_available(self, parceiro_id: int | None = None) -> list[dict]:
        cupons = self.coupons.list_available(parceiro_id)
        result = []
        for cupom in cupons:
            campanha = None
            if cupom.campanha_id:
                campanha = self.coupons.get_campanha(cupom.campanha_id)
            result.append(self._serialize_cupom(cupom, campanha))
        return result

    def list_resgatados(self, usuario_id: int) -> list[dict]:
        resgates = self.coupons.list_resgatados(usuario_id)
        result = []
        for resgate in resgates:
            cupom = self.coupons.get_by_id(resgate.cupom_id)
            campanha = self.coupons.get_campanha(cupom.campanha_id) if cupom and cupom.campanha_id else None
            result.append(
                {
                    "id": resgate.id,
                    "data_resgate": resgate.data_resgate.isoformat(),
                    "cupom": self._serialize_cupom(cupom, campanha) if cupom else None,
                }
            )
        return result

    def redeem(self, cupom_id: int, usuario_id: int, parceiro_id: int | None = None) -> dict:
        if self.coupons.already_redeemed(cupom_id, usuario_id):
            return {"success": False, "error": "Cupom já resgatado"}

        cupom = self.coupons.get_by_id(cupom_id)
        if not cupom:
            return {"success": False, "error": "Cupom não encontrado"}
        if parceiro_id and cupom.parceiro_id != parceiro_id:
            return {"success": False, "error": "Cupom não pertence a esta loja/parceiro."}
        if cupom.quantidade_disponivel <= 0:
            return {"success": False, "error": "Cupom não disponível"}

        if cupom.campanha_id:
            campanha = self.coupons.get_campanha(cupom.campanha_id)
            if campanha:
                hoje = date.today()
                if campanha.ativa is False:
                    return {"success": False, "error": "Campanha inativa"}
                if campanha.data_inicio and hoje < campanha.data_inicio:
                    return {"success": False, "error": "Campanha ainda não começou"}
                if campanha.data_fim and hoje > campanha.data_fim:
                    return {"success": False, "error": "Campanha encerrada"}

        if cupom.data_validade and date.today() > cupom.data_validade:
            return {"success": False, "error": "Cupom expirado"}

        self.coupons.redeem(cupom, usuario_id)
        return {"success": True, "message": "Cupom resgatado com sucesso!"}

    def campanhas_parceiro(self, parceiro_id: int) -> list[dict]:
        cupons = self.coupons.list_by_parceiro(parceiro_id)
        campanhas_map = {}
        for cupom in cupons:
            if cupom.campanha_id and cupom.campanha_id not in campanhas_map:
                campanha = self.coupons.get_campanha(cupom.campanha_id)
                if campanha:
                    campanhas_map[campanha.id] = campanha
        return [self._serialize_campanha(c) for c in campanhas_map.values()]

    def contagem_por_campanha(self, parceiro_id: int) -> dict:
        cupons = self.coupons.list_by_parceiro(parceiro_id)
        contagem = {}
        for cupom in cupons:
            key = str(cupom.campanha_id or 0)
            contagem[key] = contagem.get(key, 0) + (cupom.quantidade_disponivel or 0)
        return contagem

    def _serialize_campanha(self, campanha: Campanha) -> dict:
        return {
            "id": campanha.id,
            "nome": campanha.nome,
            "descricao": campanha.descricao,
            "data_inicio": campanha.data_inicio.isoformat() if campanha.data_inicio else None,
            "data_fim": campanha.data_fim.isoformat() if campanha.data_fim else None,
            "ativa": campanha.ativa,
            "criada_em": campanha.criada_em.isoformat() if campanha.criada_em else None,
        }

    def _serialize_cupom(self, cupom: Cupom, campanha: Campanha | None) -> dict:
        return {
            "id": cupom.id,
            "codigo": cupom.codigo,
            "descricao": cupom.descricao,
            "data_validade": cupom.data_validade.isoformat() if cupom.data_validade else None,
            "quantidade_disponivel": cupom.quantidade_disponivel,
            "campanha_id": cupom.campanha_id,
            "parceiro_id": cupom.parceiro_id,
            "campanha": self._serialize_campanha(campanha) if campanha else None,
        }
