# Aparas Tracker

Pequeno programa em Python para registar os sacos de aparas que gasto no meu cavalo e avisar a professora de equitação por WhatsApp, sem me esquecer.

## Porquê?

Tenho um cavalo e gastamos aparas para a box. Todos os fins de semana tinha de dizer à professora de equitação quantos sacos tinha usado, para ela poder contar e fazermos as contas dos pagamentos.

O problema: **esquecia-me quase sempre**. Depois ficava a tentar lembrar-me de quantos tinham sido, em que dias, e se já tinha pago o mês anterior ou não.

Em vez de depender da memória, fiz isto: escrevo só o número de sacos, e o programa trata do resto, da data, da hora, das contas, do estado de pagamento e da mensagem.

## O que faz

- **Regista um uso**: só tenho de dizer quantos sacos gastei. O dia e a hora vêm do relógio do PC.
- **Envia WhatsApp automaticamente** com o uso de hoje e o resumo completo.
- **Marca meses como pagos** e avisa a professora do que acabei de pagar.
- **Mostra o resumo** de todos os meses: total de sacos, o que está pago, o que falta pagar e cada uso individual.
- **Diz o mês em que mais gastei.**
- **Envia o resumo à professora** quando eu quiser, com a data de hoje.

## Como funciona

O menu tem 4 opções:

```
1 - Registar uso
2 - Marcar mês como pago
3 - Ver resumo
0 - Sair
```

- **Opção 1**: pergunta quantos sacos usei, guarda o registo e envia a mensagem.
- **Opção 2**: mostra o resumo, pergunta o mês (1-12) e o ano (Enter = ano atual), marca como pagos os usos ainda por pagar e envia a mensagem de pagamento.
- **Opção 3**: mostra o resumo e pergunta se quero enviá-lo à professora.

### O estado de pagamento é por uso

Cada uso tem o seu próprio `pago`. Assim, se o mês já estava pago e eu gastar mais um saco, esse saco aparece como "por pagar" e o mês mostra algo como `pagos: 6, por pagar: 1`.

### Exemplo de mensagem

```
Olá! Hoje, dia 18 de outubro, usámos 1 saco de aparas.

Resumo geral

Outubro de 2026: 2 sacos (por pagar)
- dia 9 às 19:30: 1 saco (por pagar)
- dia 16 às 19:30: 1 saco (por pagar)

Mês com mais uso: outubro de 2026 (2 sacos)
```

## Estrutura dos dados

Tudo fica guardado em `registos.json` (criado automaticamente na primeira utilização):

```json
{
  "2026-10": {
    "sacos": 2,
    "usos": [
      {"dia": 9, "hora": "19:30", "sacos": 1, "pago": false},
      {"dia": 16, "hora": "19:30", "sacos": 1, "pago": false}
    ]
  }
}
```

Cada mês tem o total de sacos e a lista de usos com dia, hora, quantidade e estado de pagamento.

Se existir um `registos.json` num formato antigo, o programa converte-o sozinho ao arrancar.

## Estrutura do projeto

```
.
├── main.py          # todo o código
├── registos.json    # dados (não se encontra em conjunto com o programa uma vez que é pessoal e difere de pessoa para pessoa)
└── README.md
```

As funções principais em `main.py`:

| Função | O que faz |
|---|---|
| `carregar_registos` / `guardar_registos` | Ler e escrever o JSON |
| `registar_uso` | Soma ao mês atual e guarda dia/hora |
| `marcar_pago` | Marca como pagos os usos por pagar de um mês |
| `construir_resumo` | Gera o texto do resumo (ecrã e WhatsApp) |
| `enviar_whatsapp` | Envio genérico pelo WhatsApp Web |
| `enviar_mensagem`, `enviar_mensagem_pagamento`, `enviar_mensagem_resumo` | As três mensagens diferentes |

## Como usar

1. Instalar a dependência:
   ```bash
   pip install pywhatkit
   ```
2. Em `main.py`, trocar o número em `NUMERO_PROFESSORA` pelo número real (com indicativo, por exemplo `+351...`).
3. Ter o **WhatsApp Web com sessão iniciada** no browser.
4. Correr:
   ```bash
   python main.py
   ```

## Notas

- O envio usa o [`pywhatkit`](https://pypi.org/project/pywhatkit/), que abre o WhatsApp Web no browser e envia a mensagem. Por isso o programa espera uns 15 segundos de cada vez que envia (`wait_time` em `enviar_whatsapp`).
- Não é uma API oficial do WhatsApp, por isso depende do browser estar aberto e com sessão iniciada.

## Ideias para o futuro

- Limitar o resumo enviado aos últimos meses, para a mensagem não crescer para sempre
- Lembrete automático ao fim de semana
- Ler o número de telefone de uma variável de ambiente em vez de o ter no código
