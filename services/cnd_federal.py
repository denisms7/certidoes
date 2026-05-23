import requests
import base64
import time
from pathlib import Path


def consultar_cnd(
    tipo_contribuinte: int,
    contribuinte_consulta: str,
    codigo_identificacao: str,
    token: str,
    output_path: str = "certidao.pdf",
    max_retries: int = 10,
    retry_delay: float = 1.0,
) -> dict:
    """
    Consulta a API CND e salva o PDF da certidão em disco.

    Args:
        tipo_contribuinte: 1 = Pessoa Jurídica, 2 = Pessoa Física, 3 = Imóvel Rural
        contribuinte_consulta: CNPJ (14 dígitos), CPF (11 dígitos) ou NIRF (8 dígitos)
        codigo_identificacao: 9201 = PJ, 9202 = PF, 9203 = Imóvel Rural
        token: Bearer token de autenticação
        output_path: Caminho onde o PDF será salvo
        max_retries: Número máximo de tentativas em caso de status 7
        retry_delay: Tempo de espera (segundos) entre tentativas (mínimo 0.5s)

    Returns:
        dict com Status, Mensagem e caminho do PDF salvo (se houver)

    Raises:
        ValueError: Parâmetros inválidos
        requests.HTTPError: Erros HTTP não recuperáveis
    """

    URL = "https://gateway.apiserpro.serpro.gov.br/consulta-cnd/v2/certidao"

    if retry_delay < 0.5:
        raise ValueError("retry_delay deve ser pelo menos 0.5 segundos (500ms).")

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "TipoContribuinte": tipo_contribuinte,
        "ContribuinteConsulta": contribuinte_consulta,
        "CodigoIdentificacao": codigo_identificacao,
        "GerarCertidaoPdf": True,
    }

    chave = None

    for tentativa in range(1, max_retries + 1):
        if chave:
            payload["Chave"] = chave

        print(f"[Tentativa {tentativa}/{max_retries}] Consultando API CND...")
        response = requests.post(URL, json=payload, headers=headers, timeout=30)

        # Erros HTTP não recuperáveis
        if response.status_code in (400, 401, 403, 404, 415, 500, 504):
            response.raise_for_status()

        data = response.json()
        status = data.get("Status")
        mensagem = data.get("Mensagem", "")

        print(f"  Status: {status} | {mensagem}")

        # Certidão disponível (encontrada ou emitida)
        if status in (1, 2):
            certidao = data.get("Certidao", {})
            pdf_b64 = certidao.get("DocumentoPdf")

            if pdf_b64:
                pdf_bytes = base64.b64decode(pdf_b64)
                Path(output_path).write_bytes(pdf_bytes)
                print(f"  PDF salvo em: {output_path}")
                return {
                    "Status": status,
                    "Mensagem": mensagem,
                    "Certidao": certidao,
                    "PdfSalvoEm": output_path,
                }
            else:
                print("  Aviso: certidão retornada sem PDF.")
                return {"Status": status, "Mensagem": mensagem, "Certidao": certidao}

        # Ainda em processamento — repetir com a chave
        elif status == 7:
            chave = data.get("Chave")
            print(f"  Aguardando {retry_delay}s antes de nova tentativa...")
            time.sleep(retry_delay)
            continue

        # Análise inconsistente ou base indisponível — repetir sem chave
        elif status in (5, 6):
            chave = None
            payload.pop("Chave", None)
            print(f"  Aguardando {retry_delay}s antes de nova tentativa...")
            time.sleep(retry_delay)
            continue

        # Certidão não pôde ser emitida (status 3, 4 ou outros erros)
        else:
            return {"Status": status, "Mensagem": mensagem}

    raise TimeoutError(
        f"Número máximo de tentativas ({max_retries}) atingido sem resposta definitiva."
    )


# ---------------------------------------------------------------------------
# Exemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    resultado = consultar_cnd(
        tipo_contribuinte=1,           # Pessoa Jurídica
        contribuinte_consulta="00000000000001",
        codigo_identificacao="9201",
        token="SEU_TOKEN_AQUI",
        output_path="certidao_cnd.pdf",
    )
    print(resultado)