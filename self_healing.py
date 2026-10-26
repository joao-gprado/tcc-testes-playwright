import json
import os
import time
from datetime import datetime

from google import genai
from google.genai import errors, types
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

MODELO_PADRAO = "gemini-3.8-flash"
LIMIAR_PADRAO = 80

INSTRUCOES = """Você é o componente de self-healing de uma suíte de testes Playwright.
Um passo do teste não pôde ser executado porque o seletor CSS original não encontrou exatamente um elemento na página.
Analise o HTML atual e indique um seletor CSS que aponte, de forma única, para o elemento que o passo pretendia usar.

Regras:
- O seletor deve ser CSS válido e corresponder a exatamente um elemento do HTML.
- Só atribua confiança alta se o elemento tiver a mesma função e o mesmo contexto do original (mesmo texto, mesmo rótulo, mesma posição lógica) e não existir outro candidato plausível.
- Se dois ou mais elementos forem candidatos igualmente plausíveis, a ambiguidade deve resultar em confiança baixa.
- Se o elemento não existir mais na página, devolva seletor vazio e confiança 0.
- confianca é um inteiro de 0 a 100."""

ESQUEMA_RESPOSTA = {
    "type": "object",
    "properties": {
        "seletor": {"type": "string"},
        "confianca": {"type": "integer", "minimum": 0, "maximum": 100},
        "justificativa": {"type": "string"},
    },
    "required": ["seletor", "confianca", "justificativa"],
}


class CuraAbortada(AssertionError):
    pass


class MiddlewareSelfHealing:
    def __init__(self, page, arquivo_eventos, contexto, limiar=LIMIAR_PADRAO,
                 modelo=MODELO_PADRAO, espera_ms=5000):
        self.page = page
        self.arquivo_eventos = arquivo_eventos
        self.contexto = contexto
        self.limiar = limiar
        self.modelo = modelo
        self.espera_ms = espera_ms
        self._cliente = None

    def clicar(self, seletor, intencao):
        self._resolver("clicar", seletor, intencao).click()

    def preencher(self, seletor, valor, intencao):
        self._resolver(f"preencher com '{valor}'", seletor, intencao).fill(valor)

    def marcar(self, seletor, intencao):
        self._resolver("marcar", seletor, intencao).check()

    def _resolver(self, acao, seletor, intencao):
        # Caminho normal: o seletor original encontra exatamente um elemento
        problema = self._problema(seletor, self.espera_ms)
        if problema is None:
            return self.page.locator(seletor)

        # Falhou: envia DOM e ação para a LLM
        resposta, latencia, tentativas = self._consultar_llm(acao, seletor, intencao, problema)
        novo = resposta["seletor"].strip()
        confianca = resposta["confianca"]

        if confianca < self.limiar:
            decisao = "abortado_confianca"
        elif not novo or novo == seletor or self._problema(novo, 0) is not None:
            decisao = "abortado_seletor_invalido"
        else:
            decisao = "curado"

        self._registrar({
            "acao": acao,
            "intencao": intencao,
            "seletor_original": seletor,
            "problema": problema,
            "seletor_sugerido": novo,
            "confianca": confianca,
            "justificativa": resposta["justificativa"],
            "decisao": decisao,
            "latencia_llm_s": round(latencia, 3),
            "tentativas_api": tentativas,
        })

        if decisao != "curado":
            raise CuraAbortada(
                f"Self-healing abortado ({decisao}): '{seletor}' -> '{novo}' "
                f"com confiança {confianca}% (limiar {self.limiar}%). {resposta['justificativa']}"
            )
        return self.page.locator(novo)

    def _problema(self, seletor, espera_ms):
        localizador = self.page.locator(seletor)
        try:
            if espera_ms:
                localizador.first.wait_for(state="attached", timeout=espera_ms)
            quantidade = localizador.count()
        except PlaywrightTimeoutError:
            quantidade = 0
        except PlaywrightError:
            return "seletor inválido"
        if quantidade == 0:
            return "nenhum elemento encontrado"
        if quantidade > 1:
            return f"{quantidade} elementos encontrados"
        return None

    def _consultar_llm(self, acao, seletor, intencao, problema):
        prompt = (
            f"Ação do teste: {acao}\n"
            f"Intenção do passo: {intencao}\n"
            f"Seletor original: {seletor}\n"
            f"Problema: {problema}\n\n"
            f"HTML atual da página:\n{self.page.content()}"
        )
        config = types.GenerateContentConfig(
            system_instruction=INSTRUCOES,
            response_mime_type="application/json",
            response_json_schema=ESQUEMA_RESPOSTA,
        )
        # Cota gratuita: em caso de limite de requisições (429) ou servidor sobrecarregado (500/503),
        # espera e tenta de novo; a latência registrada é só a da tentativa que deu certo
        for tentativa in range(1, 5):
            inicio = time.perf_counter()
            try:
                resposta = self._cliente_llm().models.generate_content(
                    model=self.modelo, contents=prompt, config=config
                )
                latencia = time.perf_counter() - inicio
                return json.loads(resposta.text), latencia, tentativa
            except errors.APIError as erro:
                if erro.code not in (429, 500, 503) or tentativa == 4:
                    raise
                time.sleep(20 * tentativa)

    def _cliente_llm(self):
        if self._cliente is None:
            chave = os.environ.get("GEMINI_API_KEY")
            if not chave:
                raise RuntimeError("Defina a variável de ambiente GEMINI_API_KEY para usar o self-healing.")
            self._cliente = genai.Client(api_key=chave)
        return self._cliente

    def _registrar(self, evento):
        registro = {
            "data_hora": datetime.now().isoformat(timespec="seconds"),
            **self.contexto,
            "modelo": self.modelo,
            "limiar": self.limiar,
            **evento,
        }
        self.arquivo_eventos.parent.mkdir(parents=True, exist_ok=True)
        with open(self.arquivo_eventos, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
