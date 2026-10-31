"""
main.py
Gerenciador de Modos de Câmera - Sprint 4 (Computational Thinking with Python)

Para executar:  python main.py
"""

from api import ErroClima, buscar_cidades, descrever_cidade, sugerir_modo_para_local
from armazenamento import (
    carregar_slots,
    salvar_slots,
    modo_padrao,
    slot_personalizado,
    slots_com_estado,
)
from interface import (
    confirmar,
    descrever_valor,
    escolher_numero,
    exibir_menu,
    exibir_modo,
    ler_inteiro,
    localizar_configuracao,
    pedir_novo_valor,
)




def editar_valores(modo_original: dict[str, int]) -> dict[str, int] | None:
    """
    Loop de edição sobre uma CÓPIA do modo.
    Retorna o modo editado se o usuário confirmar, ou None se cancelar/não alterar.
    """
    modo = modo_original.copy()
    print("\nConfigurações atuais:")
    exibir_modo(modo)

    while True:
        entrada = input(
            "\nQual configuração deseja mudar? (número ou nome)\n"
            "[ver = mostrar valores | sair ou 0 = finalizar]: "
        ).strip().lower()

        if entrada in ("0", "sair"):
            if modo == modo_original:
                print("Nenhuma alteração foi feita.")
                return None
            print("\nValores finais:")
            exibir_modo(modo)
            if confirmar("Deseja confirmar as alterações?"):
                return modo
            print("Alterações canceladas.")
            return None

        if entrada in ("ver", "view"):
            exibir_modo(modo)
            continue

        nome = localizar_configuracao(entrada)
        if nome is None:
            print("Configuração inválida. Digite um número de 1 a 16 ou o nome.")
            continue

        modo[nome] = pedir_novo_valor(nome)
        print(f"{nome} atualizado para {descrever_valor(nome, modo[nome])}.")




def opcao_criar(slots: dict[int, dict[str, int]]) -> None:
    """Opção 1: criar um modo em um slot livre."""
    livres = slots_com_estado(slots, personalizado=False)
    if not livres:
        print("Todos os slots já estão em uso. Use Editar ou Excluir.")
        return

    print(f"Slots livres: {', '.join(map(str, livres))}")
    numero = escolher_numero(livres, "Em qual slot deseja criar o modo? ")

    novo = editar_valores(slots[numero])
    if novo is None:
        return

    slots[numero] = novo
    if salvar_slots(slots):
        print(f"Modo salvo no slot {numero}!")


def opcao_editar(slots: dict[int, dict[str, int]]) -> None:
    """Opção 2: editar um slot que já tem modo salvo."""
    usados = slots_com_estado(slots, personalizado=True)
    if not usados:
        print("Nenhum modo salvo para editar.")
        return

    print(f"Slots com modo salvo: {', '.join(map(str, usados))}")
    numero = escolher_numero(usados, "Qual slot deseja editar? ")

    editado = editar_valores(slots[numero])
    if editado is None:
        return

    slots[numero] = editado
    if salvar_slots(slots):
        print(f"Slot {numero} atualizado!")


def opcao_excluir(slots: dict[int, dict[str, int]]) -> None:
    """Opção 3: resetar um slot para o padrão."""
    usados = slots_com_estado(slots, personalizado=True)
    if not usados:
        print("Nenhum modo salvo para excluir.")
        return

    print(f"Slots com modo salvo: {', '.join(map(str, usados))}")
    numero = escolher_numero(usados, "Qual slot deseja excluir? ")

    if confirmar(f"Tem certeza que deseja excluir o slot {numero}?"):
        slots[numero] = modo_padrao()
        if salvar_slots(slots):
            print(f"Slot {numero} foi resetado para o padrão.")
    else:
        print("Operação cancelada.")


def opcao_listar(slots: dict[int, dict[str, int]]) -> None:
    """Opção 4: mostrar os modos salvos."""
    usados = slots_com_estado(slots, personalizado=True)
    if not usados:
        print("Nenhum modo salvo ainda.")
        return

    for numero in usados:
        print(f"\n--- Slot {numero} ---")
        exibir_modo(slots[numero])


def escolher_cidade(cidades: list[dict]) -> dict | None:
    """Mostra as cidades encontradas e deixa o usuário escolher (0 cancela)."""
    if len(cidades) == 1:
        return cidades[0]

    print("\nCidades encontradas:")
    for i, cidade in enumerate(cidades, start=1):
        print(f"{i}. {descrever_cidade(cidade)}")

    numero = ler_inteiro("Qual delas? (0 para cancelar): ", 0, len(cidades))
    if numero:
        return cidades[numero - 1] 
    else:
        return None


def opcao_sugerir_clima(slots: dict[int, dict[str, int]]) -> None:
    """Opção 5: consulta o clima via API e sugere um modo de câmera."""
    nome = input("Digite a cidade (ENTER para cancelar): ").strip()
    if not nome:
        return

    try:
        cidades = buscar_cidades(nome)
        if not cidades:
            print("Cidade não encontrada. Verifique o nome e tente novamente.")
            return

        cidade = escolher_cidade(cidades)
        if cidade is None:
            print("Operação cancelada.")
            return

        descricao, sugestao = sugerir_modo_para_local(cidade["latitude"], cidade["longitude"])
    except ErroClima as erro:
        print(erro)
        return

    print(f"\nClima em {descrever_cidade(cidade)}: {descricao}")
    print("Modo sugerido:")
    exibir_modo(sugestao)

    if not confirmar("\nDeseja salvar essa sugestão em um slot?"):
        return

    livres = slots_com_estado(slots, personalizado=False)
    if livres:
        print(f"Slots livres: {', '.join(map(str, livres))}")
    numero = escolher_numero(list(slots), "Em qual slot deseja salvar? ")

    if slot_personalizado(slots, numero) and not confirmar(
        f"O slot {numero} já tem um modo. Deseja substituir?"
    ):
        print("Operação cancelada.")
        return

    slots[numero] = sugestao
    if salvar_slots(slots):
        print(f"Sugestão salva no slot {numero}!")




def main() -> None:
    slots = carregar_slots()

    while True:
        exibir_menu()
        escolha = ler_inteiro("Escolha uma opção: ", 1, 6)

        match escolha:
            case 1:
                opcao_criar(slots)
            case 2:
                opcao_editar(slots)
            case 3:
                opcao_excluir(slots)
            case 4:
                opcao_listar(slots)
            case 5:
                opcao_sugerir_clima(slots)
            case 6:
                if confirmar("Deseja realmente sair?"):
                    print("Saindo... Até a próxima!")
                    break
        


if __name__ == "__main__":
    main()