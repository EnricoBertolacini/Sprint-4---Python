"""
armazenamento.py
Configurações da câmera, modelo de dados dos slots e persistência em JSON.
Este módulo não depende de nenhum outro arquivo do projeto.
"""

import json
from pathlib import Path

ARQUIVO_JSON = Path(__file__).with_name("modos.json")
TOTAL_SLOTS = 5


CONFIGURACOES = {
    "Brilho":              {"id": 1,  "min": 0, "max": 100, "padrao": 50},
    "Saturação":           {"id": 2,  "min": 0, "max": 100, "padrao": 50},
    "Temperatura de Cor":  {"id": 3,  "min": 0, "max": 100, "padrao": 50},
    "Contraste":           {"id": 4,  "min": 0, "max": 100, "padrao": 50},
    "Exposição":           {"id": 5,  "min": 0, "max": 100, "padrao": 50},
    "Sombra":              {"id": 6,  "min": 0, "max": 100, "padrao": 50},
    "Nitidez":             {"id": 7,  "min": 0, "max": 100, "padrao": 50},
    "Flash":               {"id": 8,  "min": 0, "max": 2, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado", 2: "Automático"}},
    "Formato de Arquivo":  {"id": 9,  "min": 1, "max": 5, "padrao": 1,
                            "opcoes": {1: "JPEG", 2: "PNG", 3: "RAW", 4: "TIFF", 5: "HEIC"}},
    "Proporção":           {"id": 10, "min": 1, "max": 5, "padrao": 1,
                            "opcoes": {1: "4:3", 2: "16:9", 3: "1:1", 4: "16:10", 5: "21:9"}},
    "Modo Documento":      {"id": 11, "min": 0, "max": 1, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado"}},
    "Digitalizar Texto":   {"id": 12, "min": 0, "max": 1, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado"}},
    "Traduzir Texto":      {"id": 13, "min": 0, "max": 1, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado"}},
    "Scanner QR":          {"id": 14, "min": 0, "max": 1, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado"}},
    "Timer em Segundos":   {"id": 15, "min": 0, "max": 60, "padrao": 0},
    "Pesquisa via Lens":   {"id": 16, "min": 0, "max": 1, "padrao": 0,
                            "opcoes": {0: "Desligado", 1: "Ligado"}},
}




def modo_padrao() -> dict[str, int]:
    """Retorna um modo novo com todos os valores padrão."""
    return {nome: cfg["padrao"] for nome, cfg in CONFIGURACOES.items()}


def modo_valido(modo: object) -> bool:
    """Confere se um modo lido do JSON tem todas as chaves e valores dentro da faixa."""
    if not isinstance(modo, dict) or set(modo) != set(CONFIGURACOES):
        return False
    return all(
        isinstance(valor, int)
        and CONFIGURACOES[nome]["min"] <= valor <= CONFIGURACOES[nome]["max"]
        for nome, valor in modo.items()
    )


def slot_personalizado(slots: dict[int, dict[str, int]], numero: int) -> bool:
    """True se o slot foi modificado (é diferente do padrão)."""
    return slots[numero] != modo_padrao()


def slots_com_estado(slots: dict[int, dict[str, int]], personalizado: bool) -> list[int]:
    """Lista os números de slots personalizados (True) ou livres (False)."""
    return [n for n in slots if slot_personalizado(slots, n) == personalizado]




def carregar_slots() -> dict[int, dict[str, int]]:
    """Lê os slots do arquivo JSON. Se não existir ou estiver corrompido, usa o padrão."""
    slots = {n: modo_padrao() for n in range(1, TOTAL_SLOTS + 1)}

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        return slots  # primeira execução: ainda não há arquivo
    except (json.JSONDecodeError, OSError):
        print("Aviso: não foi possível ler o arquivo de modos. Iniciando com slots vazios.")
        return slots

    for n in slots:
        modo = dados.get(str(n)) if isinstance(dados, dict) else None
        if modo_valido(modo):
            slots[n] = modo
    return slots


def salvar_slots(slots: dict[int, dict[str, int]]) -> bool:
    """Grava os slots no arquivo JSON. Retorna True se deu certo."""
    try:
        with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
            json.dump({str(n): m for n, m in slots.items()},
                      arquivo, indent=4, ensure_ascii=False)
        return True
    except OSError as erro:
        print(f"Erro ao salvar o arquivo: {erro}")
        return False