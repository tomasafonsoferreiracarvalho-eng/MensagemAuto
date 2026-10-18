import json
import os
from datetime import datetime

import pywhatkit  # pip install pywhatkit

FICHEIRO = "registos.json"
NUMERO_PROFESSORA = "+351*********"  # <- muda para o número real (com +351)

MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
         "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]


def nome_mes(chave):
    """'2026-10' -> 'outubro de 2026'"""
    ano, mes = chave.split("-")
    return f"{MESES[int(mes) - 1]} de {ano}"


def sacos_txt(n):
    """1 -> '1 saco', 2 -> '2 sacos'"""
    return f"{n} saco" if n == 1 else f"{n} sacos"


def carregar_registos():
    """Lê o JSON. Se não existir, devolve {}. Converte formatos antigos."""
    if not os.path.exists(FICHEIRO):
        return {}
    with open(FICHEIRO, "r", encoding="utf-8") as f:
        dados = json.load(f)

    mudou = False

    if isinstance(dados, list):  # formato 1 (lista) -> por mês
        novo = {}
        for r in dados:
            chave = f"{r['ano']}-{r['mes']:02d}"
            m = novo.setdefault(chave, {"sacos": 0, "usos": []})
            m["sacos"] += r["sacos"]
            m["usos"].append({"dia": r["dia"], "hora": r["hora"],
                              "sacos": r["sacos"], "pago": r.get("pago", False)})
        dados, mudou = novo, True

    # formato 2 (pago por mês) -> pago por uso
    for m in dados.values():
        for u in m["usos"]:
            if "pago" not in u:
                u["pago"] = m.get("pago", False)
                mudou = True
        if "pago" in m:
            del m["pago"]
            mudou = True

    if mudou:
        guardar_registos(dados)
    return dados


def guardar_registos(dados):
    with open(FICHEIRO, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def estado_mes(m):
    """Estado do mês calculado a partir dos usos."""
    pagos = sum(u["sacos"] for u in m["usos"] if u["pago"])
    por_pagar = m["sacos"] - pagos
    if por_pagar == 0:
        return "tudo pago"
    if pagos == 0:
        return "por pagar"
    return f"pagos: {pagos}, por pagar: {por_pagar}"


def construir_resumo(dados):
    """Devolve o resumo completo em texto (usado no ecrã e no WhatsApp)."""
    if not dados:
        return "Ainda não há registos."

    linhas = []
    for chave in sorted(dados):
        m = dados[chave]
        linhas.append(f"*{nome_mes(chave).capitalize()}*: {sacos_txt(m['sacos'])} "
                      f"({estado_mes(m)})")
        for u in m["usos"]:
            estado = "pago" if u["pago"] else "por pagar"
            linhas.append(f"- dia {u['dia']} às {u['hora']}: "
                          f"{sacos_txt(u['sacos'])} ({estado})")
        linhas.append("")

    mais = max(dados, key=lambda c: dados[c]["sacos"])
    linhas.append(f"Mês com mais uso: {nome_mes(mais)} ({sacos_txt(dados[mais]['sacos'])})")
    return "\n".join(linhas)


def enviar_whatsapp(texto):
    """Envio genérico pelo WhatsApp Web."""
    pywhatkit.sendwhatmsg_instantly(NUMERO_PROFESSORA, texto,
                                    wait_time=15, tab_close=True)


def enviar_mensagem(sacos, dia, mes, dados):
    """Mensagem de uso: uso de hoje + resumo completo."""
    texto = (f"Olá Ana! Hoje, dia {dia} de {MESES[mes - 1]}, "
             f"usámos {sacos_txt(sacos)} de aparas.\n\n"
             f"*Resumo geral*\n\n{construir_resumo(dados)}"
             f"Mensagem automática👌\n\n")
    enviar_whatsapp(texto)


def enviar_mensagem_pagamento(chave, sacos_pagos, dados):
    """Mensagem de pagamento: o que foi pago + resumo completo."""
    texto = (f"Olá Ana! Já paguei {sacos_txt(sacos_pagos)} de aparas de "
             f"{nome_mes(chave)}.\n\n"
             f"*Resumo geral*\n\n{construir_resumo(dados)}"
             f"Mensagem automática👌\n\n")
    enviar_whatsapp(texto)


def enviar_mensagem_resumo(dados):
    """Mensagem só com o resumo, até ao dia de hoje."""
    agora = datetime.now()
    texto = (f"Olá Ana! Aqui vai um resumo até ao dia de hoje "
             f"({agora.day} de {MESES[agora.month - 1]}) de {agora.year}.\n\n"
             f"*Resumo geral*\n\n{construir_resumo(dados)}"
             f"Mensagem automática👌\n\n")
    enviar_whatsapp(texto)


def registar_uso(sacos):
    """Soma ao mês atual, guarda dia/hora (por pagar) e envia mensagem."""
    agora = datetime.now()
    chave = f"{agora.year}-{agora.month:02d}"

    dados = carregar_registos()
    mes = dados.setdefault(chave, {"sacos": 0, "usos": []})
    mes["sacos"] += sacos
    mes["usos"].append({"dia": agora.day, "hora": agora.strftime("%H:%M"),
                        "sacos": sacos, "pago": False})
    guardar_registos(dados)

    enviar_mensagem(sacos, agora.day, agora.month, dados)


def marcar_pago(numero_mes, ano):
    """Marca como pagos os usos ainda por pagar desse mês e avisa."""
    chave = f"{ano}-{numero_mes:02d}"
    dados = carregar_registos()
    if chave not in dados:
        print(f"Não há registos para {nome_mes(chave)}.")
        return

    por_pagar = [u for u in dados[chave]["usos"] if not u["pago"]]
    if not por_pagar:
        print(f"{nome_mes(chave)} já estava tudo pago.")
        return

    sacos_pagos = sum(u["sacos"] for u in por_pagar)
    for u in por_pagar:
        u["pago"] = True
    guardar_registos(dados)
    print(f"{nome_mes(chave)}: marcados como pagos -> {sacos_txt(sacos_pagos)}.")

    enviar_mensagem_pagamento(chave, sacos_pagos, dados)


def mostrar_resumo():
    print("\n--- Resumo ---\n")
    print(construir_resumo(carregar_registos()))
    print()


def menu():
    while True:
        print("1 - Registar uso\n2 - Marcar mês como pago\n3 - Ver resumo\n0 - Sair")
        opcao = input("Opção: ").strip()

        if opcao == "":  # Enter perdido (ex.: do pywhatkit) -> ignora
            continue
        if opcao == "1":
            registar_uso(int(input("Quantos sacos usaste? ")))
        elif opcao == "2":
            mostrar_resumo()
            mes = int(input("Já pagaste qual mês? (número 1-12): "))
            ano_txt = input(f"De que ano? (Enter = {datetime.now().year}): ").strip()
            ano = int(ano_txt) if ano_txt else datetime.now().year
            marcar_pago(mes, ano)
        elif opcao == "3":
            mostrar_resumo()
            if input("Enviar à professora? (s/n): ").strip().lower() == "s":
                enviar_mensagem_resumo(carregar_registos())
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    menu()