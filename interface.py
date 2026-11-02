"""
interface.py
Entrada de dados validada (try/except) e exibição de informações no terminal.
"""

from armazenamento import CONFIGURACOES




def ler_inteiro(mensagem: str, minimo: int, maximo: int) -> int:
    while True:
        try:
            valor = int(input(mensagem))
        except ValueError:
            print("Entrada inválida. Digite apenas números inteiros.")
            continue

        if minimo <= valor <= maximo:
            return valor
        print(f"Valor fora da faixa. Digite um número entre {minimo} e {maximo}.")


def confirmar(mensagem: str) -> bool:
    while True:
        resposta = input(f"{mensagem} (S/N): ").strip().upper()
        if resposta in ("S", "Y"):
            return True
        if resposta == "N":
            return False
        print("Opção inválida. Digite S para sim ou N para não.")


def escolher_numero(validos: list[int], mensagem: str) -> int:
    while True:
        numero = ler_inteiro(mensagem, min(validos), max(validos))
        if numero in validos:
            return numero
        print("Escolha um dos slots listados.")


def localizar_configuracao(entrada: str) -> str | None:
    entrada = entrada.strip().lower()
    for nome, cfg in CONFIGURACOES.items():
        if entrada == str(cfg["id"]) or entrada == nome.lower():
            return nome
    return None


def pedir_novo_valor(nome: str) -> int:
    cfg = CONFIGURACOES[nome]
    print(f"\n{nome}: valores de {cfg['min']} a {cfg['max']}")
    for valor, significado in cfg.get("opcoes", {}).items():
        print(f"  {valor} = {significado}")
    return ler_inteiro("Novo valor: ", cfg["min"], cfg["max"])




def descrever_valor(nome: str, valor: int) -> str:
    opcoes = CONFIGURACOES[nome].get("opcoes")
    return f"{valor} ({opcoes[valor]})" if opcoes else str(valor)


def exibir_modo(modo: dict[str, int]) -> None:
    for nome, valor in modo.items():
        print(f"  {CONFIGURACOES[nome]['id']:>2} - {nome}: {descrever_valor(nome, valor)}")


def exibir_menu() -> None:
    print("\n==========================================")
    print("        MODOS DA CÂMERA")
    print("==========================================")
    print("1. Criar um modo")
    print("2. Editar um modo")
    print("3. Excluir um modo")
    print("4. Ver modos salvos")
    print("5. Sugerir modo pelo clima (API)")
    print("6. Sair")
    print("------------------------------------------")