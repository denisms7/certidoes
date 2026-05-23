from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

def gerar_cnd_federal(cnpj: str):
    cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()

    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    stealth(
        driver,
        languages=["pt-BR", "pt"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    def human_sleep(min_s=0.4, max_s=1.0):
        time.sleep(random.uniform(min_s, max_s))

    def human_type(element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.08, 0.22))

    try:
        driver.get("https://servicos.receitafederal.gov.br/servico/certidoes/#/home/cnpj")
        wait = WebDriverWait(driver, 30)
        human_sleep(4, 6)

        # ── 1. CNPJ ──────────────────────────────────────────────────
        campo_cnpj = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='niContribuinte']"))
        )
        ActionChains(driver).move_to_element(campo_cnpj).perform()
        human_sleep()
        campo_cnpj.click()
        human_sleep()
        human_type(campo_cnpj, cnpj)
        print(f"✅ CNPJ digitado: {campo_cnpj.get_attribute('value')}")
        human_sleep(1, 2)

        # ── 2. Emitir Certidão ───────────────────────────────────────
        btn_emitir = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.br-button.primary.btn-acao[type='submit']"
            ))
        )
        ActionChains(driver).move_to_element(btn_emitir).perform()
        human_sleep()
        driver.execute_script("arguments[0].click();", btn_emitir)
        print("✅ Botão 'Emitir Certidão' clicado!")
        human_sleep(2, 4)

        # ── 3. Modal: Consultar Certidão (secondary) ─────────────────
        btn_consultar_modal = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.br-button.secondary.btn-acao"
            ))
        )
        ActionChains(driver).move_to_element(btn_consultar_modal).perform()
        human_sleep()
        driver.execute_script("arguments[0].click();", btn_consultar_modal)
        print("✅ Botão 'Consultar Certidão' (modal) clicado!")
        human_sleep(2, 3)

        # ── 4. Consultar Certidão (submit) ───────────────────────────
        abas_antes = set(driver.window_handles)

        btn_submit = wait.until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, "button.br-button.primary.btn-acao[type='submit']"
            ))
        )
        ActionChains(driver).move_to_element(btn_submit).perform()
        human_sleep()
        driver.execute_script("arguments[0].click();", btn_submit)
        print("✅ Botão 'Consultar Certidão' (submit) clicado!")
        human_sleep(3, 5)

        # ── 5. Nova aba? ─────────────────────────────────────────────
        try:
            WebDriverWait(driver, 8).until(
                lambda d: len(d.window_handles) > len(abas_antes)
            )
            nova_aba = (set(driver.window_handles) - abas_antes).pop()
            driver.switch_to.window(nova_aba)
            print(f"✅ Nova aba: {driver.current_url}")
        except Exception:
            print("ℹ️  Permanecendo na aba atual.")

        # ── 6. Aguarda tabela ────────────────────────────────────────
        print("⏳ Aguardando tabela...")
        human_sleep(3, 5)

        tabela_ok = False
        for seletor in ["datatable-body-row", ".datatable-body-row", "datatable-body", "ngx-datatable"]:
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, seletor))
                )
                print(f"✅ Tabela: '{seletor}'")
                tabela_ok = True
                break
            except Exception:
                print(f"   ⚠️ '{seletor}' não encontrado...")

        if not tabela_ok:
            print("❌ Tabela não encontrada. HTML atual:")
            print(driver.page_source[:3000])
            return

        human_sleep(2, 3)

        # ── 7. Baixa certidão Válida ──────────────────────────────────
        linhas = driver.find_elements(By.CSS_SELECTOR, "datatable-body-row")
        print(f"✅ {len(linhas)} linha(s) encontrada(s).")

        baixou = False
        for i, linha in enumerate(linhas):
            status = ""
            for span in linha.find_elements(By.CSS_SELECTOR, "datatable-body-cell span"):
                titulo = span.get_attribute("title") or ""
                if titulo in ("Válida", "Expirada", "Inválida"):
                    status = titulo
                    break

            print(f"   Linha {i+1} → '{status}'")

            if status == "Válida":
                btn_dl = linha.find_element(
                    By.CSS_SELECTOR, "button.br-button.small.circle[title='Segunda via']"
                )
                ActionChains(driver).move_to_element(btn_dl).perform()
                human_sleep()
                driver.execute_script("arguments[0].click();", btn_dl)
                print("✅ Download iniciado!")
                baixou = True
                break

        if not baixou:
            print("⚠️  Nenhuma certidão 'Válida' encontrada.")

        time.sleep(5)

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("🔒 Navegador fechado.")

if __name__ == "__main__":
    gerar_cnd_federal("75845503000167")