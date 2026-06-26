from kapitour_shared.banco_dados import BaseModelo, motor_banco


def executar_migracoes() -> None:
    BaseModelo.metadata.create_all(bind=motor_banco)
