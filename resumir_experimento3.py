import csv
import json
import statistics
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "resultados" / "experimento3"
CONJUNTOS = ["controle", "v1", "v2", "v3"]


def ler_resultados_testes():
    # junit_<conjunto>_r<rodada>.xml -> {(conjunto, teste): [aprovado, ...]}
    resultados = defaultdict(list)
    for arquivo in sorted(PASTA.glob("junit_*.xml")):
        conjunto = arquivo.stem.split("_")[1]
        for caso in ET.parse(arquivo).iter("testcase"):
            teste = caso.get("name").replace("[chromium]", "")
            falhou = caso.find("failure") is not None or caso.find("error") is not None
            resultados[(conjunto, teste)].append(not falhou)
    return resultados


def ler_eventos():
    arquivo = PASTA / "eventos.jsonl"
    if not arquivo.exists():
        return []
    with open(arquivo, encoding="utf-8") as f:
        return [json.loads(linha) for linha in f if linha.strip()]


def main():
    resultados = ler_resultados_testes()
    eventos = ler_eventos()

    linhas = []
    for conjunto in CONJUNTOS:
        execucoes = [ok for (c, _), lista in resultados.items() if c == conjunto for ok in lista]
        if not execucoes:
            continue
        ev = [e for e in eventos if e["conjunto"] == conjunto]
        latencias = [e["latencia_llm_s"] for e in ev]
        linhas.append({
            "conjunto": conjunto,
            "execucoes_de_teste": len(execucoes),
            "aprovados": sum(execucoes),
            "reprovados": len(execucoes) - sum(execucoes),
            "chamadas_llm": len(ev),
            "curados": sum(e["decisao"] == "curado" for e in ev),
            "abortados_confianca": sum(e["decisao"] == "abortado_confianca" for e in ev),
            "abortados_seletor_invalido": sum(e["decisao"] == "abortado_seletor_invalido" for e in ev),
            "confianca_media": round(statistics.mean(e["confianca"] for e in ev), 1) if ev else "",
            "latencia_media_s": round(statistics.mean(latencias), 2) if latencias else "",
            "latencia_min_s": round(min(latencias), 2) if latencias else "",
            "latencia_max_s": round(max(latencias), 2) if latencias else "",
        })

    with open(PASTA / "resumo.csv", "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.DictWriter(f, fieldnames=list(linhas[0].keys()), delimiter=";")
        escritor.writeheader()
        escritor.writerows(linhas)

    with open(PASTA / "resumo_por_teste.csv", "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";")
        escritor.writerow(["conjunto", "teste", "rodadas", "aprovados", "decisoes_llm", "confiancas"])
        for (conjunto, teste), lista in sorted(resultados.items()):
            ev = [e for e in eventos if e["conjunto"] == conjunto and e["teste"] == teste]
            escritor.writerow([
                conjunto, teste, len(lista), sum(lista),
                ", ".join(e["decisao"] for e in ev),
                ", ".join(str(e["confianca"]) for e in ev),
            ])

    cabecalho = list(linhas[0].keys())
    print("| " + " | ".join(cabecalho) + " |")
    print("|" + "---|" * len(cabecalho))
    for linha in linhas:
        print("| " + " | ".join(str(v) for v in linha.values()) + " |")
    print(f"\nResumo salvo em {PASTA / 'resumo.csv'} e {PASTA / 'resumo_por_teste.csv'}")


if __name__ == "__main__":
    main()
