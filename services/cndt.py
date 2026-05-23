import requests
import re
import os
from datetime import datetime


def consultar_cndt(cnpj: str, token: str = None) -> dict:
    """
    Consulta a Certidão Negativa de Débitos Trabalhistas (CNDT)
    do Tribunal Superior do Trabalho (TST) para um dado CNPJ.

    Args:
        cnpj  : CNPJ com ou sem formatação (ex: "00.000.000/0001-00")
        token : Token de acesso à API da Infosimples.
                Se None, lê a variável de ambiente INFOSIMPLES_TOKEN.

    Returns:
        dict com todos os campos retornados pela API, mais:
            - "_pdf_path"  : caminho do PDF salvo (ou None)
            - "_raw"       : resposta JSON completa da API
    """
    # ── 1. Normaliza o CNPJ ──────────────────────────────────────────
    cnpj_limpo = re.sub(r"\D", "", cnpj)
    if len(cnpj_limpo) != 14:
        raise ValueError(f"CNPJ inválido: '{cnpj}'. Esperado 14 dígitos.")

    # ── 2. Resolve o token ───────────────────────────────────────────
    if token is None:
        token = os.environ.get("INFOSIMPLES_TOKEN")
    if not token:
        raise EnvironmentError(
            "Token não fornecido. Passe 'token=...' ou defina "
            "a variável de ambiente INFOSIMPLES_TOKEN."
        )

    # ── 3. Chama a API ───────────────────────────────────────────────
    url = "https://api.infosimples.com/api/v2/consultas/tribunal/tst/cndt"
    payload = {
        "cnpj" : cnpj_limpo,
        "token": token,
    }

    resp = requests.post(url, data=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # ── 4. Verifica status da API ────────────────────────────────────
    code = data.get("code")
    if code not in (200, 206):
        raise RuntimeError(
            f"API retornou código {code}: {data.get('errors') or data}"
        )

    resultado = (data.get("data") or [{}])[0]

    # ── 5. Baixa o PDF da certidão (quando disponível) ───────────────
    pdf_path = None
    url_certidao = resultado.get("certidao")
    conseguiu     = resultado.get("conseguiu_emitir_certidao_negativa")

    if url_certidao and conseguiu:
        try:
            pdf_resp = requests.get(url_certidao, timeout=60)
            pdf_resp.raise_for_status()

            data_emissao = resultado.get("emissao_data", "")
            sufixo = data_emissao.replace("/", "-") if data_emissao else \
                     datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_path = f"CNDT_{cnpj_limpo}_{sufixo}.pdf"

            with open(pdf_path, "wb") as f:
                f.write(pdf_resp.content)

            print(f"✔ Certidão salva em: {pdf_path}")
        except Exception as e:
            print(f"⚠ Não foi possível baixar o PDF: {e}")

    resultado["_pdf_path"] = pdf_path
    resultado["_raw"]      = data
    return resultado


# ── Exemplo de uso ────────────────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = "SEU_TOKEN_AQUI"   # ou use a variável de ambiente
    CNPJ  = "00.000.000/0001-00"

    info = consultar_cndt(CNPJ, token=TOKEN)

    print("Nome          :", info.get("nome"))
    print("CNPJ          :", info.get("cnpj"))
    print("Consta        :", info.get("consta"))
    print("Validade      :", info.get("validade"))
    print("Código certidão:", info.get("certidao_codigo"))
    print("PDF salvo em  :", info.get("_pdf_path") or "—")