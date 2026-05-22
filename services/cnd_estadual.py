"""
Script: certidao_fazenda_pr.py

Descrição:
    Gera automaticamente a Certidão
    da Fazenda do Paraná.

Prefeitura Municipal de Centenário do Sul
Setor de Informática
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import (
    ActionChains
)
from selenium.webdriver.support.ui import (
    WebDriverWait
)
from selenium.webdriver.support import (
    expected_conditions as EC
)
from selenium.common.exceptions import (
    TimeoutException
)
from webdriver_manager.chrome import (
    ChromeDriverManager
)

from dotenv import load_dotenv

import os
import time
import base64
import random


load_dotenv()


# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

URL = (
    "https://cdwfazenda.paas.pr.gov.br/"
    "cdwportal/certidao/automatica"
)

PASTA_DOWNLOAD = os.getenv(
    "PASTA_DOWNLOAD",
    os.path.join(
        os.path.expanduser("~"),
        "Downloads",
        "Certidoes"
    )
)

os.makedirs(
    PASTA_DOWNLOAD,
    exist_ok=True
)


# ─────────────────────────────────────────────
# DELAY HUMANO
# ─────────────────────────────────────────────

def esperar(
    minimo: float = 1.5,
    maximo: float = 4.0
) -> None:
    """
    Delay aleatório para simular uso humano.
    """

    time.sleep(
        random.uniform(minimo, maximo)
    )


# ─────────────────────────────────────────────
# CHROME
# ─────────────────────────────────────────────

def configurar_chrome() -> webdriver.Chrome:
    """
    Configura Chrome para automação.
    """

    opcoes = webdriver.ChromeOptions()

    opcoes.add_argument("--start-maximized")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")

    # Anti automação
    opcoes.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    opcoes.add_experimental_option(
        "excludeSwitches",
        [
            "enable-automation",
            "enable-logging"
        ]
    )

    opcoes.add_experimental_option(
        "useAutomationExtension",
        False
    )

    # User agent real
    opcoes.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/136.0.0.0 Safari/537.36"
    )

    # NÃO usar headless
    # opcoes.add_argument("--headless=new")

    servico = Service(
        ChromeDriverManager().install()
    )

    driver = webdriver.Chrome(
        service=servico,
        options=opcoes
    )

    # Remove webdriver flag
    driver.execute_script("""
    Object.defineProperty(
        navigator,
        'webdriver',
        {
            get: () => undefined
        }
    )
    """)

    return driver


# ─────────────────────────────────────────────
# CLIQUE HUMANO
# ─────────────────────────────────────────────

def clique_humano(
    driver: webdriver.Chrome,
    elemento
) -> None:
    """
    Simula clique humano.
    """

    ActionChains(driver)\
        .move_to_element(elemento)\
        .pause(random.uniform(0.5, 1.5))\
        .click()\
        .perform()


# ─────────────────────────────────────────────
# DIGITAÇÃO HUMANA
# ─────────────────────────────────────────────

def digitar_humano(
    campo,
    texto: str
) -> None:
    """
    Digita lentamente.
    """

    for caractere in texto:

        campo.send_keys(caractere)

        time.sleep(
            random.uniform(0.05, 0.20)
        )


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

    with open(
        caminho_pdf,
        "wb"
    ) as arquivo:

        arquivo.write(
            base64.b64decode(
                pdf["data"]
            )
        )

    print("✔ PDF salvo com sucesso.")


# ─────────────────────────────────────────────
# PROCESSO PRINCIPAL
# ─────────────────────────────────────────────

def gerar_certidao_fazenda_pr(
    cnpj: str
) -> str | None:
    """
    Gera certidão da Fazenda PR.
    """

    cnpj = "".join(
        filter(str.isdigit, cnpj)
    )

    nome_arquivo = (
        f"certidao_fazenda_pr_{cnpj}.pdf"
    )

    caminho_pdf = os.path.join(
        PASTA_DOWNLOAD,
        nome_arquivo
    )

    print("=" * 60)
    print(" FAZENDA PR — CERTIDÃO")
    print(f" CNPJ    : {cnpj}")
    print(f" Destino : {caminho_pdf}")
    print("=" * 60)

    driver = configurar_chrome()

    wait = WebDriverWait(
        driver,
        60
    )

    try:

        # ─────────────────────────────────────
        # 1. ABRE PORTAL
        # ─────────────────────────────────────

        print("\n[1/5] Abrindo portal...")

        driver.get(URL)

        wait.until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        esperar(3, 6)

        # ─────────────────────────────────────
        # 2. PREENCHE CNPJ
        # ─────────────────────────────────────

        print("[2/5] Preenchendo CNPJ...")

        campo_cnpj = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'input[aria-label="CPF ou CNPJ do requerente"]'
                )
            )
        )

        campo_cnpj.clear()

        esperar()

        digitar_humano(
            campo_cnpj,
            cnpj
        )

        esperar(2, 4)

        # ─────────────────────────────────────
        # 3. EMITIR CERTIDÃO
        # ─────────────────────────────────────

        print("[3/5] Emitindo certidão...")

        botoes_emitir = wait.until(
            EC.presence_of_all_elements_located(
                (
                    By.XPATH,
                    "//span[contains(text(),'Emitir Certidão')]"
                )
            )
        )

        botao_emitir = botoes_emitir[0]

        clique_humano(
            driver,
            botao_emitir
        )

        esperar(4, 7)

        # ─────────────────────────────────────
        # 4. SOLICITAR NOVA CERTIDÃO
        # ─────────────────────────────────────

        print(
            "[4/5] Solicitando nova certidão..."
        )

        botao_solicitar = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),"
                    "'Solicitar nova certidão')]"
                )
            )
        )

        clique_humano(
            driver,
            botao_solicitar
        )

        esperar(5, 8)

        # ─────────────────────────────────────
        # 5. BAIXAR PDF
        # ─────────────────────────────────────

        print("[5/5] Abrindo PDF...")

        botao_pdf = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//span[contains(text(),'Baixar PDF')]"
                )
            )
        )

        clique_humano(
            driver,
            botao_pdf
        )

        esperar(5, 8)

        # ─────────────────────────────────────
        # NOVA ABA
        # ─────────────────────────────────────

        abas = driver.window_handles

        if len(abas) > 1:

            driver.switch_to.window(
                abas[-1]
            )

            esperar(3, 5)

        # ─────────────────────────────────────
        # SALVA PDF
        # ─────────────────────────────────────

        salvar_pdf(
            driver,
            caminho_pdf
        )

        # ─────────────────────────────────────
        # FINALIZAÇÃO
        # ─────────────────────────────────────

        if os.path.exists(caminho_pdf):

            tamanho = (
                os.path.getsize(
                    caminho_pdf
                ) / 1024
            )

            print(
                "\n✅ CERTIDÃO GERADA COM SUCESSO"
            )

            print(
                f"📄 Arquivo : {caminho_pdf}"
            )

            print(
                f"📦 Tamanho : {tamanho:.1f} KB"
            )

            return caminho_pdf

        raise FileNotFoundError(
            "PDF não encontrado."
        )

    except TimeoutException:

        print(
            "\n❌ TEMPO DE ESPERA EXCEDIDO"
        )

        raise

    except Exception as erro:

        print(
            "\n❌ ERRO DURANTE EXECUÇÃO"
        )

        print(f"Erro: {erro}")

        raise

    finally:

        esperar(2, 4)

        driver.quit()

        print(
            "\n🛑 Navegador encerrado."
        )


# ─────────────────────────────────────────────
# ALIAS
# ─────────────────────────────────────────────

gerar_certidao_pr = (
    gerar_certidao_fazenda_pr
)


# ─────────────────────────────────────────────
# EXECUÇÃO DIRETA
# ─────────────────────────────────────────────

if __name__ == "__main__":

    gerar_certidao_fazenda_pr(
        "75845503000167"
    )