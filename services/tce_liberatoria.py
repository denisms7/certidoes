from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

from dotenv import load_dotenv

import os
import time
import base64


load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

PASTA_DOWNLOAD = os.getenv(
    "PASTA_DOWNLOAD",
    os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "Certidoes_TCE_PR"
    )
)

os.makedirs(PASTA_DOWNLOAD, exist_ok=True)


# ─────────────────────────────────────────────
# CHROME
# ─────────────────────────────────────────────

def configurar_chrome() -> webdriver.Chrome:
    """
    Configura o Chrome para automação.
    """

    opcoes = webdriver.ChromeOptions()

    opcoes.add_argument("--start-maximized")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")

    # Evita problemas em ambientes automatizados
    opcoes.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    # Descomente para rodar sem abrir navegador
    # opcoes.add_argument("--headless=new")

    servico = Service(
        ChromeDriverManager().install()
    )

    driver = webdriver.Chrome(
        service=servico,
        options=opcoes
    )

    return driver


# ─────────────────────────────────────────────
# ALERT
# ─────────────────────────────────────────────

def aceitar_alerta(driver: webdriver.Chrome) -> bool:
    """
    Aceita o alert do TCE-PR se existir.
    """

    try:
        WebDriverWait(driver, 10).until(
            EC.alert_is_present()
        )

        alerta = driver.switch_to.alert

        print(f"\n⚠ ALERTA ENCONTRADO:")
        print(f"   {alerta.text}")

        alerta.accept()

        print("✔ Alert confirmado com sucesso.")

        return True

    except TimeoutException:
        print("ℹ Nenhum alert encontrado.")
        return False


# ─────────────────────────────────────────────
# GERAR PDF
# ─────────────────────────────────────────────

def salvar_pdf(
    driver: webdriver.Chrome,
    caminho_pdf: str
) -> None:
    """
    Gera PDF diretamente via Chrome DevTools.
    """

    print("\n🖨 Gerando PDF...")

    pdf = driver.execute_cdp_cmd(
        "Page.printToPDF",
        {
            "printBackground": True,
            "landscape": False,
            "paperWidth": 8.27,
            "paperHeight": 11.69,
            "marginTop": 0.2,
            "marginBottom": 0.2,
            "marginLeft": 0.2,
            "marginRight": 0.2,
        }
    )

    with open(caminho_pdf, "wb") as arquivo:
        arquivo.write(
            base64.b64decode(pdf["data"])
        )

    print("✔ PDF salvo com sucesso.")


# ─────────────────────────────────────────────
# PROCESSO PRINCIPAL
# ─────────────────────────────────────────────

def gerar_liberatoria_tce(cnpj: str) -> str:
    """
    Gera a certidão liberatória do TCE-PR
    para o CNPJ informado.

    Retorna o caminho do PDF gerado.
    """

    # Remove caracteres não numéricos
    cnpj = "".join(filter(str.isdigit, cnpj))

    url = (
        "https://servicos.tce.pr.gov.br/"
        "TCEPR/Tribunal/CertidaoLiberatoria/"
        f"srv_certidao_emissao.aspx?nrCNPJ={cnpj}"
    )

    nome_arquivo = f"certidao_liberatoria_{cnpj}.pdf"

    caminho_pdf = os.path.join(
        PASTA_DOWNLOAD,
        nome_arquivo
    )

    print("=" * 60)
    print(" TCE-PR — Certidão Liberatória")
    print(f" CNPJ    : {cnpj}")
    print(f" Destino : {caminho_pdf}")
    print("=" * 60)

    driver = configurar_chrome()

    try:

        # ─────────────────────────────────────
        # 1. ABRE PORTAL
        # ─────────────────────────────────────

        print("\n[1/5] Abrindo portal do TCE-PR...")

        driver.get(url)

        # ─────────────────────────────────────
        # 2. ALERTA
        # ─────────────────────────────────────

        print("[2/5] Verificando alertas...")

        aceitar_alerta(driver)

        # ─────────────────────────────────────
        # 3. AGUARDA CARREGAMENTO
        # ─────────────────────────────────────

        print("[3/5] Aguardando carregamento da página...")

        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        time.sleep(3)

        # ─────────────────────────────────────
        # 4. GERA PDF
        # ─────────────────────────────────────

        print("[4/5] Gerando certidão em PDF...")

        salvar_pdf(driver, caminho_pdf)

        # ─────────────────────────────────────
        # 5. FINALIZAÇÃO
        # ─────────────────────────────────────

        print("[5/5] Finalizando...")

        if os.path.exists(caminho_pdf):

            tamanho = os.path.getsize(
                caminho_pdf
            ) / 1024

            print("\n✅ CERTIDÃO GERADA COM SUCESSO")
            print(f"📄 Arquivo : {caminho_pdf}")
            print(f"📦 Tamanho : {tamanho:.1f} KB")

            return caminho_pdf

        else:
            raise FileNotFoundError(
                "O PDF não foi encontrado."
            )

    except Exception as erro:

        print("\n❌ ERRO DURANTE EXECUÇÃO")
        print(f"Erro: {erro}")

        raise

    finally:

        time.sleep(2)

        driver.quit()

        print("\n🛑 Navegador encerrado.")


# ─────────────────────────────────────────────
# ALIAS PARA IMPORTAÇÃO
# ─────────────────────────────────────────────

gerar_liberatoria = gerar_liberatoria_tce


# ─────────────────────────────────────────────
# EXECUÇÃO DIRETA
# ─────────────────────────────────────────────

if __name__ == "__main__":

    cnpj = "75845503000167"

    gerar_liberatoria_tce(cnpj)