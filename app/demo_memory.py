"""Demonstracao real de memoria conversacional com seis turnos sinteticos."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from app.chain import build_chat


TURNS = [
    "Dados sinteticos desta conversa: minha frota se chama Atlas. Guarde esse nome.",
    "O veiculo sintetico que estamos acompanhando e o T01.",
    "A saida prevista desse veiculo e 19:00. Ainda nao temos cronograma validado.",
    "Explique brevemente a diferenca entre recomendacao e decisao do gestor.",
    "Qual e a MMS do modo Equilibrado V1? Responda em uma frase.",
    "Usando apenas o que informei nesta conversa, lembre o nome da frota, "
    "o ID do veiculo e o horario de saida. Nao invente um cronograma.",
]


def run(output, limit=1200):
    output = Path(output)
    if output.exists():
        raise FileExistsError("Saida existente: escolha outro caminho.")
    if limit < 1:
        raise ValueError("Limite deve ser positivo.")
    chat = build_chat(limit=limit)
    records = []
    for index, text in enumerate(TURNS, 1):
        started = time.perf_counter()
        record = {"turn": index, "input": text, "response": None, "error": None}
        try:
            result = chat.invoke({"input": text})
            record["response"] = result.get("response")
            record["status"] = "response_received"
        except Exception as exc:
            record["error"] = {"type": type(exc).__name__,
                               "message": "Falha na chamada; detalhes sensiveis omitidos."}
            record["status"] = "error"
        record["latency_seconds"] = time.perf_counter() - started
        try:
            memory = chat.memory.load_memory_variables({})
            snapshot = {key: str(value) for key, value in memory.items()}
            record["memory_snapshot"] = snapshot
            record["memory_tokens_estimated"] = chat.memory.llm.get_num_tokens_from_messages(
                chat.memory.chat_memory.messages
            )
        except Exception as exc:
            record["memory_inspection_error"] = {
                "type": type(exc).__name__,
                "message": "Falha ao inspecionar memoria; detalhes sensiveis omitidos.",
            }
        records.append(record)
        print(f"Turno {index}: {record['status']}")
        print(record["response"] or record["error"])
        if record["error"]:
            # Nao continuar uma conversa cuja sequencia de memoria ficou incompleta.
            break
    last = records[-1]
    response = str(last.get("response") or "") if last["turn"] == 6 else ""
    report = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic": True, "memory_limit_tokens": limit,
        "completed_turns": sum(r["status"] == "response_received" for r in records),
        "lexical_checks_final_response": {"fleet_Atlas": "atlas" in response.lower(),
                                          "vehicle_T01": "t01" in response.lower(),
                                          "departure_19h": "19:00" in response or "19h" in response.lower()},
        "limitations": [
            "Checagens lexicais sao auxiliares; revisar o texto integral.",
            "Seis turnos curtos podem nao acionar a poda de 1200 tokens.",
            "Tokens estimados e memoria visivel nao garantem o contexto efetivo do provedor.",
            "Esta demonstracao nao e teste do motor nem prova de context rot.",
        ], "records": records,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, default=str)
    print(f"Evidencia: {output}")
    return report


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", default="evidence/demo_memory.json")
    cli.add_argument("--limit", type=int, default=1200)
    args = cli.parse_args()
    run(args.output, args.limit)


if __name__ == "__main__":
    main()
