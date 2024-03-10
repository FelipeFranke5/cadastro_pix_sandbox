"""Extração dos MIDs para rodar o script."""


def extracao_lista_mids() -> list[str]:
    """Retorna a lista de MIDs obtida na extração do arquivo."""
    with open('lista_mid.txt', encoding='utf-8') as arq:
        lista = arq.read().splitlines()
        return lista
