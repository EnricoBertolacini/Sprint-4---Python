"""
api_clima.py
Integração com a API externa Open-Meteo (gratuita e sem chave).
Converte o clima atual de uma cidade em um modo de câmera sugerido.
"""

from contextlib import contextmanager

import requests

from armazenamento import modo_padrao

URL_GEOCODING = "https://geocoding-api.open-meteo.com/v1/search"
URL_CLIMA = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_API = 8  
MAX_RESULTADOS = 5  


class ErroClima(Exception):
    """Erro ao consultar a API. A mensagem já é própria para mostrar ao usuário."""


@contextmanager
def _traduzir_erros():
    try:
        yield
    except requests.exceptions.Timeout as erro:
        raise ErroClima("A consulta demorou demais. Tente novamente em instantes.") from erro
    except requests.exceptions.ConnectionError as erro:
        raise ErroClima("Sem conexão com a internet. Verifique sua rede.") from erro
    except requests.exceptions.RequestException as erro:
        raise ErroClima(f"Erro ao acessar a API: {erro}") from erro
    except (KeyError, ValueError, TypeError) as erro:
        raise ErroClima("A API retornou dados inesperados. Tente novamente mais tarde.") from erro


def buscar_cidades(nome: str) -> list[dict]:
    with _traduzir_erros():
        resposta = requests.get(
            URL_GEOCODING,
            params={"name": nome, "count": MAX_RESULTADOS, "language": "pt"},
            timeout=TIMEOUT_API,
        )
        resposta.raise_for_status()
        resultados = resposta.json().get("results") or []
        return [
            {
                "nome": r["name"],
                "estado": r.get("admin1", ""),
                "pais": r.get("country", ""),
                "latitude": r["latitude"],
                "longitude": r["longitude"],
            }
            for r in resultados
        ]


def descrever_cidade(cidade: dict) -> str:
    detalhes = ", ".join(p for p in (cidade["estado"], cidade["pais"]) if p)
    if detalhes:
        return f"{cidade['nome']} - {detalhes}"  
    else:
        return cidade["nome"]


def buscar_clima(latitude: float, longitude: float) -> dict:
    with _traduzir_erros():
        resposta = requests.get(
            URL_CLIMA,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "cloud_cover,is_day,precipitation",
            },
            timeout=TIMEOUT_API,
        )
        resposta.raise_for_status()
        return resposta.json()["current"]


def montar_sugestao(clima: dict) -> tuple[str, dict[str, int]]:
    sugestao = modo_padrao()
    nuvens = clima["cloud_cover"]

    if not clima["is_day"]:
        descricao = "Noite"
        sugestao.update({"Brilho": 70, "Exposição": 75, "Sombra": 40,
                         "Nitidez": 40, "Flash": 2})
    elif clima["precipitation"] > 0 or nuvens > 70:
        descricao = "Dia nublado ou chuvoso"
        sugestao.update({"Brilho": 65, "Contraste": 55, "Exposição": 60,
                         "Temperatura de Cor": 40, "Flash": 2})
    elif nuvens > 25:
        descricao = "Dia parcialmente nublado"
        sugestao.update({"Brilho": 55, "Contraste": 55, "Exposição": 50})
    else:
        descricao = "Dia ensolarado"
        sugestao.update({"Brilho": 40, "Contraste": 60, "Exposição": 40,
                         "Temperatura de Cor": 60, "Flash": 0})

    return f"{descricao} (nuvens: {nuvens}%)", sugestao


def sugerir_modo_para_local(latitude: float, longitude: float) -> tuple[str, dict[str, int]]:
    clima = buscar_clima(latitude, longitude)
    with _traduzir_erros():
        return montar_sugestao(clima)