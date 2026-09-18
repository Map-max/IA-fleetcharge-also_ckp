"""Experimento sintetico controlado; requer acesso real ao Ollama configurado."""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, ConfigDict, Field

from app.chain import build_llm
from app.memory_manager import count_tokens
from app.prompts import SYSTEM_PROMPT


class SyntheticAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    fleet: str = Field(description="Nome da frota do registro relevante")
    vehicle: str = Field(description="ID do veiculo do registro relevante")
    departure: str = Field(description="Saida no formato HH:MM")
    minimum_margin_minutes: int = Field(description="MMS em minutos")


EXPECTED = {
    "fleet": "Atlas",
    "vehicle": "T01",
    "departure": "19:00",
    "minimum_margin_minutes": 120,
}
FACTS = (
    "REGISTRO RELEVANTE SINTETICO: frota Atlas; veiculo T01; "
    "saida prevista 19:00; MMS obrigatoria 120 minutos. "
    "Estes fatos sao dados de teste, nao resultados do motor."
)
QUESTION = "Extraia somente os quatro campos do REGISTRO RELEVANTE SINTETICO."
TARGETS = (2000, 4000, 8000)


def write_exclusive(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as handle:
        handle.write(data)


def run(output, repetitions=3):
    output = Path(output)
    table_path = output.with_suffix(".md")
    if output == table_path:
        raise ValueError("Use extensao .json para a saida.")
    if output.exists() or table_path.exists():
        raise FileExistsError("Saida existente: escolha outro caminho; nada sera sobrescrito.")
    if repetitions < 1:
        raise ValueError("Repeticoes devem ser positivas.")

    parser = PydanticOutputParser(pydantic_object=SyntheticAnswer)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("system", "Experimento sintetico de extracao. Ignore distratores. "
         "Responda somente segundo o esquema: {format_instructions}"),
        ("human", "{facts}\n\nDISTRATORES SEM RELACAO:\n{noise}\n\n{question}"),
    ]).partial(format_instructions=parser.get_format_instructions())
    base = {"facts": FACTS, "question": QUESTION}

    def estimated(noise):
        return count_tokens(prompt.invoke({**base, "noise": noise}).to_string())

    contexts = []
    noise = ""
    # Cada contexto preserva o anterior; fatos ficam na mesma posicao inicial.
    for target in TARGETS:
        index = 1
        while estimated(noise) < target:
            addition = f"Arquivo decorativo {index}: a sala possui mapas, cadernos e cadeiras.\n"
            if estimated(noise + addition) > target:
                break
            noise += addition
            index += 1
        contexts.append({"target_tokens": target, "estimated_input_tokens": estimated(noise),
                         "noise": noise, "target_exceeded_by_fixed_prompt": estimated("") > target})

    lengths = [item["estimated_input_tokens"] for item in contexts]
    if not all(left < right for left, right in zip(lengths, lengths[1:])):
        raise ValueError("Experimento cancelado antes das chamadas: sao necessarios tres "
                         "comprimentos de contexto distintos e crescentes. Reduza o prompt fixo.")

    llm = build_llm()
    records = []
    for context in contexts:
        inputs = {**base, "noise": context["noise"]}
        rendered = prompt.invoke(inputs).to_string()
        for repetition in range(1, repetitions + 1):
            captured = {}

            def capture(message):
                captured["raw"] = message.content
                captured["response_metadata"] = getattr(message, "response_metadata", {})
                captured["usage_metadata"] = getattr(message, "usage_metadata", None)
                return message

            # Pipeline LCEL completo; captura antes do parser preserva respostas invalidas.
            chain = prompt | llm | RunnableLambda(capture) | parser
            started = time.perf_counter()
            record = {"target_tokens": context["target_tokens"],
                      "estimated_input_tokens": context["estimated_input_tokens"],
                      "target_exceeded_by_fixed_prompt": context["target_exceeded_by_fixed_prompt"],
                      "repetition": repetition, "prompt": rendered,
                      "parsed": None, "error": None, "exact_match": False}
            try:
                answer = chain.invoke(inputs).model_dump()
                record["parsed"] = answer
                record["exact_match"] = answer == EXPECTED
                record["field_matches"] = {key: answer.get(key) == value for key, value in EXPECTED.items()}
            except Exception as exc:
                record["error"] = {"type": type(exc).__name__,
                                   "message": "Falha na chamada ou no parsing; detalhes sensiveis omitidos."}
            record["latency_seconds"] = time.perf_counter() - started
            record.update(captured)
            records.append(record)

    successful_calls = [r for r in records if "raw" in r]
    summary = []
    for target in TARGETS:
        group = [r for r in records if r["target_tokens"] == target]
        summary.append({"target": target, "estimated_tokens": group[0]["estimated_input_tokens"],
                        "calls": len(group), "responses_received": sum("raw" in r for r in group),
                        "exact_matches": sum(r["exact_match"] for r in group),
                        "errors": sum(r["error"] is not None for r in group)})
    comparable = all(row["responses_received"] == repetitions for row in summary)
    decline = comparable and any(row["exact_matches"] < summary[0]["exact_matches"] for row in summary[1:])
    conclusion = (
        "Queda de acerto observada nesta amostra; nao demonstra causalidade ou degradacao geral."
        if decline else "Degradacao nao observada nas respostas desta amostra."
    ) if comparable else "Execucao incompleta: nao permite concluir sobre degradacao."
    result = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "experiment": "context_rot_synthetic_direct_lcel", "synthetic": True,
        "model": getattr(llm, "model", None), "temperature": getattr(llm, "temperature", None),
        "expected": EXPECTED, "repetitions": repetitions, "summary": summary,
        "conclusion": conclusion, "received_responses": len(successful_calls),
        "limitations": [
            "Tokens sao estimativa tiktoken; nao equivalem necessariamente ao tokenizer do modelo.",
            "Alvos incluem o prompt inteiro; prefixo fixo pode exceder um alvo e isso e registrado.",
            "Sem truncamento local e sem memoria de conversa neste experimento.",
            "Truncamento remoto nao e observavel com certeza; metadados disponiveis sao preservados.",
            "Nao confundir perda de memoria por poda com context rot.",
            "Tres repeticoes nao sustentam conclusao estatistica; ordem dos contextos e fixa.",
            "Falha de rede/autenticacao/parser nao e automaticamente context rot.",
        ], "records": records,
    }
    write_exclusive(output, json.dumps(result, ensure_ascii=False, indent=2, default=str))
    lines = ["# Experimento de contexto sintetico", "", conclusion, "",
             "| Alvo | Tokens estimados | Respostas | Acertos exatos | Erros |",
             "|---:|---:|---:|---:|---:|"]
    lines += [f"| {r['target']} | {r['estimated_tokens']} | {r['responses_received']}/{r['calls']} | {r['exact_matches']} | {r['errors']} |" for r in summary]
    lines += ["", "Sem truncamento local. Tokens estimados; resultados nao validam o motor de recarga.",
              "Consulte o JSON para prompts, respostas brutas, metadados e limitacoes."]
    write_exclusive(table_path, "\n".join(lines) + "\n")
    print(f"Evidencias: {output} e {table_path}")
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", default="evidence/context_rot.json")
    cli.add_argument("--repetitions", type=int, default=3)
    args = cli.parse_args()
    run(args.output, args.repetitions)


if __name__ == "__main__":
    main()
