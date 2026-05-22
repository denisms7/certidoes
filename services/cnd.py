from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def gerar_cnd_federal(cnpj: str):
    # Remove formatação caso venha com máscara (ex: 75.845.503/0001-67)
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        driver.get("https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj")

        wait = WebDriverWait(driver, 20)
        time.sleep(2)

        # ── Preenche o CNPJ ──────────────────────────────────────────
        campo_cnpj = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "input[name='niContribuinte']"
            ))
        )

        campo_cnpj.click()
        time.sleep(0.3)

        for digito in cnpj:
            campo_cnpj.send_keys(digito)
            time.sleep(0.15)

        print(f"✅ CNPJ digitado: {campo_cnpj.get_attribute('value')}")

        # ── Clica no botão "Emitir Certidão" ─────────────────────────
        btn_emitir = wait.until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR, "button.br-button.primary.btn-acao[type='submit']"
            ))
        )

        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn_emitir)
        time.sleep(0.5)

        driver.execute_script("arguments[0].click();", btn_emitir)
        print("✅ Botão 'Emitir Certidão' clicado!")

        input("Pressione ENTER para fechar...")

    except Exception as e:
        print(f"❌ Erro: {e}")

    finally:
        driver.quit()
        print("🔒 Navegador fechado.")


if __name__ == "__main__":
    gerar_cnd("75845503000167")