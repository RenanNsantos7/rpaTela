import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pyautogui
import time
import os
from dotenv import load_dotenv

load_dotenv()
url = 'https://sistema.soc.com.br/WebSoc/LoginAction.do#'
login = os.getenv('LOGIN')
senha = os.getenv('SENHA')
ID = os.getenv('id')

def configurar_driver():
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument("--disable-notifications")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("prefs", {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    })
    
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def tentar_executar(func, driver, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            func(driver)
            return True
        except Exception as e:
            print(f"[ERRO] {func.__name__} falhou ({tentativa}/{tentativas}): {e}")
            time.sleep(2)  # Espera antes de tentar novamente
            
    print(f"[FALHA] {func.__name__} não conseguiu executar após {tentativas} tentativas. Reiniciando script...\n")
    driver.quit()
    time.sleep(5)  # Espera antes de reiniciar
    main()  # Chama novamente a função principal
    return False

def fazer_login(driver):
    driver.get(url)
    campo_login = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "usu"))
    )
    campo_login.send_keys(login)
    campo_senha = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "senha"))
    )
    campo_senha.send_keys(senha)
    driver.execute_script("document.getElementById('empsoc').value = arguments[0];", ID)
    driver.execute_script("document.getElementById('bt_entrar').click();")

def agenda(driver):
    driver.execute_script("document.getElementById('cod_programa').value = arguments[0];", '236')
    driver.execute_script("document.getElementById('btn_programa').click();")
    time.sleep(2)

def clicar_botao(driver):
    driver.switch_to.frame('socframe')
    driver.execute_script("document.querySelector('#botoes > table > tbody > tr > td:nth-child(5) > a:nth-child(9) > img').click();")
    time.sleep(2)

def aplicar_filtro(driver):
    script = """
    const selectElement = document.querySelector('#filtroEspecialidadeVo');
    const option = selectElement.querySelector('option:nth-child(4)');
    option.selected = true;
    """
    driver.execute_script(script)
    filtroSala = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "filtroSala"))
    )
    filtroSala.send_keys('1')
    time.sleep(2)

def tela_chamada(driver):
    driver.execute_script("document.querySelector('#botoes > table > tbody > tr > td:nth-child(5) > a:nth-child(2) > img').click();")

def abrir_ultimas_chamadas(driver):
    driver.switch_to.default_content()
    driver.switch_to.frame('socframe')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#sim > i"))
    )
    driver.execute_script("document.querySelector('#sim > i').click();")
    pyautogui.press('F11')
    driver.switch_to.default_content()

def obter_timer(driver):
    driver.switch_to.default_content()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "timerSessao"))
    )
    elemento = driver.find_element(By.ID, "timerSessao")
    valor_timer = elemento.text
    print("[INFO] Valor do timerSessao:", valor_timer)
    return valor_timer

def monitorar_timer(driver):
    while True:
        try:
            botao_ok = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "botaoOk"))
            )
            if botao_ok:
                print("[INFO] Botão OK encontrado. Clicando...")
                botao_ok.click()
        except:
            print("[INFO] Botão OK não encontrado.")

        valor_timer = obter_timer(driver)
        if valor_timer:
            print(f"[INFO] Valor do timerSessao: {valor_timer}")
            timer_int = int(valor_timer[3:])
            if timer_int > 0 and timer_int <= 10:
                print("[ALERTA] Tempo expirando! Reiniciando o navegador...")
                driver.quit()
                time.sleep(5)
                main()
                break
            else:
                print("[INFO] Aguardando 15 segundos para nova verificação...")
                time.sleep(15)
        else:
            print("[ERRO] Falha ao obter o timer. Tentando novamente em 1 minuto...")
            time.sleep(60)

def main():
    print("\n[INFO] Iniciando automação...")
    driver = configurar_driver()
    
    if not tentar_executar(fazer_login, driver): return
    if not tentar_executar(agenda, driver): return
    if not tentar_executar(clicar_botao, driver): return
    if not tentar_executar(aplicar_filtro, driver): return
    if not tentar_executar(tela_chamada, driver): return
    if not tentar_executar(abrir_ultimas_chamadas, driver): return
    if not tentar_executar(obter_timer, driver): return
    
    monitorar_timer(driver)

if __name__ == "__main__":
    main()
