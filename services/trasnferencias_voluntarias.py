"""
Script: certidao_transferencia_voluntaria_pr.py

Descrição:
    Emite automaticamente a Certidão para
    Transferência Voluntária do Estado do Paraná.

Prefeitura Municipal de Centenário do Sul
Setor de Informática
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import (
    WebDriverWait,
    Select
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException
)

from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

import os
import time
import shutil
import base64


load_dotenv()

# ─────────────────────────────────────────────
# CONFIGURAÇÕES
# ─────────────────────────────────────────────

URL = (
    "https://www.fazenda.pr.gov.br/servicos/"
    "consultar-emitir-certidao-transferencia-voluntaria"
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
    Configura Chrome para automação.
    """

    pasta_temp = os.path.join(
        PASTA_DOWNLOAD,
        "temp_transferencia_voluntaria"
    )

    os.makedirs(pasta_temp, exist_ok=True)

    opcoes = webdriver.ChromeOptions()

    prefs = {
        "download.default_directory": pasta_temp,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
    }

    opcoes.add_experimental_option(
        "prefs",
        prefs
    )

    opcoes.add_experimental_option(
        "excludeSwitches",
        ["enable-logging"]
    )

    opcoes.add_argument("--start-maximized")
    opcoes.add_argument("--disable-gpu")
    opcoes.add_argument("--no-sandbox")
    opcoes.add_argument("--disable-dev-shm-usage")

    # EXECUÇÃO OCULTA
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
# FUNÇÃO PRINCIPAL
# ─────────────────────────────────────────────

def gerar_certidao_transferencia_voluntaria(
    cnpj: str
) -> str | None:
    """
    Gera certidão de transferência voluntária.
    """

    cnpj = "".join(filter(str.isdigit, cnpj))

    nome_arquivo = (
        f"certidao_transferencia_voluntaria_{cnpj}.pdf"
    )

    caminho_final = os.path.join(
        PASTA_DOWNLOAD,
        nome_arquivo
    )

    pasta_temp = os.path.join(
        PASTA_DOWNLOAD,
        "temp_transferencia_voluntaria"
    )

    print("=" * 60)
    print(" CERTIDÃO TRANSFERÊNCIA VOLUNTÁRIA")
    print(f" CNPJ    : {cnpj}")
    print(f" Destino : {caminho_final}")
    print("=" * 60)

    driver = configurar_chrome()

    wait = WebDriverWait(driver, 30)

    try:

        # ─────────────────────────────────────
        # 1. ABRIR PORTAL
        # ─────────────────────────────────────

        print("\n[1/7] Abrindo portal...")

        driver.get(URL)

        wait.until(
            lambda d: d.execute_script(
                "return document.readyState"
            ) == "complete"
        )

        # ─────────────────────────────────────
        # 2. FECHAR COOKIES
        # ─────────────────────────────────────

        print("[2/7] Fechando aviso de cookies...")

        try:

            botao_cookie = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(., 'Aceitar tudo')]"
                    )
                )
            )

            driver.execute_script(
                "arguments[0].click();",
                botao_cookie
            )

            print("✔ Cookies aceitos.")

            time.sleep(2)

        except Exception:

            print("⚠ Aviso de cookies não apareceu.")

        # ─────────────────────────────────────
        # 3. ENTRAR NO IFRAME
        # ─────────────────────────────────────

        print("[3/7] Entrando no formulário...")

        iframe = wait.until(
            EC.presence_of_element_located(
                (
                    By.TAG_NAME,
                    "iframe"
                )
            )
        )

        driver.switch_to.frame(iframe)

        time.sleep(2)

        # ─────────────────────────────────────
        # 4. SELECIONAR MUNICÍPIO
        # ─────────────────────────────────────

        print("[4/7] Selecionando município...")

        select_municipio = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "codMunicipio"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            select_municipio
        )

        # 618 = Centenário do Sul
        Select(select_municipio).select_by_value("618")

        print("✔ Município selecionado.")

        time.sleep(3)

        # ─────────────────────────────────────
        # 5. PREENCHER CNPJ
        # ─────────────────────────────────────

        print("[5/7] Preenchendo CNPJ...")

        campo_cnpj = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//input[@type='text']"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            campo_cnpj
        )

        campo_cnpj.click()

        campo_cnpj.clear()

        campo_cnpj.send_keys(cnpj)

        print("✔ CNPJ preenchido.")

        time.sleep(2)

        # ─────────────────────────────────────
        # 6. EMITIR CERTIDÃO
        # ─────────────────────────────────────

        print("[6/7] Emitindo certidão...")

        botao_emitir = wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//input[@type='button' and contains(@value,'Emitir')]"
                )
            )
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            botao_emitir
        )

        time.sleep(1)

        janela_principal = driver.current_window_handle

        formulario = botao_emitir.find_element(
            By.XPATH,
            "./ancestor::form"
        )

        # EXECUTA FUNÇÃO ORIGINAL DO PORTAL
        driver.execute_script(
            "Emitir(arguments[0]);",
            formulario
        )

        print("✔ Função Emitir() executada.")

        time.sleep(5)

        # ─────────────────────────────────────
        # 7. AGUARDAR POPUP
        # ─────────────────────────────────────

        print("[7/7] Aguardando popup...")

        WebDriverWait(driver, 30).until(
            EC.number_of_windows_to_be(2)
        )

        for janela in driver.window_handles:

            if janela != janela_principal:

                driver.switch_to.window(janela)

                break

        print("✔ Popup aberto.")

        # aguarda renderização completa
        time.sleep(5)

        # ─────────────────────────────────────
        # SALVAR POPUP COMO PDF
        # ─────────────────────────────────────

        print("🖨 Gerando PDF da certidão...")

        resultado = driver.execute_cdp_cmd(
            "Page.printToPDF",
            {
                "landscape": False,
                "printBackground": True,
                "preferCSSPageSize": True
            }
        )

        pdf_data = base64.b64decode(
            resultado["data"]
        )

        # remove arquivo antigo
        if os.path.exists(caminho_final):

            os.remove(caminho_final)

        with open(caminho_final, "wb") as arquivo:

            arquivo.write(pdf_data)

        print("✔ PDF salvo com sucesso.")

        print("\n✅ CERTIDÃO GERADA COM SUCESSO")
        print(f"📄 Arquivo : {caminho_final}")

        return caminho_final

    except TimeoutException:

        print("\n❌ TEMPO DE ESPERA EXCEDIDO")

        raise

    except NoSuchElementException as erro:

        print("\n❌ ELEMENTO NÃO ENCONTRADO")
        print(f"Erro: {erro}")

        raise

    except Exception as erro:

        print("\n❌ ERRO DURANTE EXECUÇÃO")
        print(f"Erro: {erro}")

        raise

    finally:

        time.sleep(2)

        driver.quit()

        # REMOVE PASTA TEMPORÁRIA
        if os.path.exists(pasta_temp):

            try:

                shutil.rmtree(pasta_temp)

                print("🗑 Pasta temporária removida.")

            except Exception as erro:

                print(
                    f"⚠ Não foi possível remover pasta temporária: {erro}"
                )

        print("\n🛑 Navegador encerrado.")


# ─────────────────────────────────────────────
# ALIAS
# ─────────────────────────────────────────────

gerar_certidao_tv = (
    gerar_certidao_transferencia_voluntaria
)

# ─────────────────────────────────────────────
# EXECUÇÃO DIRETA
# ─────────────────────────────────────────────

if __name__ == "__main__":

    gerar_certidao_transferencia_voluntaria(
        "75845503000167"
    )