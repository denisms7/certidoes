"""
Script: fgts_crf.py

Descrição:
    Gera automaticamente o Certificado de
    Regularidade do FGTS (CRF) da Caixa.

Prefeitura Municipal de Centenário do Sul
Setor de Informática
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
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

URL = (
    "https://consulta-crf.caixa.gov.br/"
    "consultacrf/pages/consultaEmpregador.jsf"
)

PASTA_DOWNLOAD = os.getenv(
    "PASTA_DOWNLOAD",
    os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "Certidoes"
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

    opcoes.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

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
# PDF
# ─────────────────────────────────────────────

def salvar_pdf(
    driver: webdriver.Chrome,
    caminho_pdf: str
) -> None:
    """
    Salva página atual em PDF.
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

def gerar_crf_fgts(cnpj: str) -> str | None:
    """
    Consulta e gera o CRF FGTS.
    """

    cnpj = "".join(filter(str.isdigit, cnpj))

    nome_arquivo = f"crf_fgts_{cnpj}.pdf"

    caminho_pdf = os.path.join(
        PASTA_DOWNLOAD,
        nome_arquivo
    )

    print("=" * 60)
    print(" CAIXA — CRF FGTS")
    print(f" CNPJ    : {cnpj}")
    print(f" Destino : {caminho_pdf}")
    print("=" * 60)

    driver = configurar_chrome()

    wait = WebDriverWait(driver, 30)

    try:

        # ─────────────────────────────────────
        # 1. ABRE SITE
        # ─────────────────────────────────────

        print("\n[1/7] Abrindo portal...")

        driver.get(URL)

        # Aguarda carregamento
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        # ─────────────────────────────────────
        # 2. PREENCHE CNPJ
        # ─────────────────────────────────────

        print("[2/7] Preenchendo CNPJ...")

        campo_cnpj = wait.until(
            EC.presence_of_element_located(
                (
                    By.ID,
                    "mainForm:txtInscricao1"
                )
            )
        )

        campo_cnpj.clear()

        campo_cnpj.send_keys(cnpj)

        # ─────────────────────────────────────
        # 3. CONSULTAR
        # ─────────────────────────────────────

        print("[3/7] Consultando...")

        botao_consultar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "mainForm:btnConsultar"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_consultar
        )

        time.sleep(5)

        # ─────────────────────────────────────
        # 4. VERIFICA CERTIDÃO
        # ─────────────────────────────────────

        print("[4/7] Verificando existência do CRF...")

        links = driver.find_elements(
            By.ID,
            "mainForm:j_id51"
        )

        if not links:

            print("\n❌ NÃO POSSUI CERTIDÃO FGTS")

            return None

        print("✔ Certidão encontrada.")

        # ─────────────────────────────────────
        # 5. ABRE CERTIDÃO
        # ─────────────────────────────────────

        print("[5/7] Abrindo certidão...")

        link_certidao = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "mainForm:j_id51"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            link_certidao
        )

        time.sleep(3)

        # ─────────────────────────────────────
        # 6. VISUALIZAR
        # ─────────────────────────────────────

        print("[6/7] Visualizando certidão...")

        botao_visualizar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "mainForm:btnVisualizar"
                )
            )
        )

        driver.execute_script(
            "arguments[0].click();",
            botao_visualizar
        )

        # Aguarda página carregar
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        time.sleep(5)

        # ─────────────────────────────────────
        # 7. GERAR PDF
        # ─────────────────────────────────────

        print("[7/7] Salvando PDF...")

        salvar_pdf(
            driver,
            caminho_pdf
        )

        # ─────────────────────────────────────
        # FINALIZAÇÃO
        # ─────────────────────────────────────

        if os.path.exists(caminho_pdf):

            tamanho = (
                os.path.getsize(caminho_pdf)
                / 1024
            )

            print("\n✅ CRF GERADO COM SUCESSO")
            print(f"📄 Arquivo : {caminho_pdf}")
            print(f"📦 Tamanho : {tamanho:.1f} KB")

            return caminho_pdf

        raise FileNotFoundError(
            "PDF não encontrado."
        )

    except TimeoutException:

        print("\n❌ TEMPO DE ESPERA EXCEDIDO")

        raise

    except Exception as erro:

        print("\n❌ ERRO DURANTE EXECUÇÃO")
        print(f"Erro: {erro}")

        raise

    finally:

        time.sleep(2)

        driver.quit()

        print("\n🛑 Navegador encerrado.")


# ─────────────────────────────────────────────
# ALIAS
# ─────────────────────────────────────────────

gerar_crf = gerar_crf_fgts


# ─────────────────────────────────────────────
# EXECUÇÃO DIRETA
# ─────────────────────────────────────────────

if __name__ == "__main__":

    gerar_crf_fgts(
        "75845503000167"
    )