import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import Select
import pyautogui

import time
import os
from dotenv import load_dotenv
from time import sleep

# Carregar variáveis de ambiente
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
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def fazer_login(driver):
    driver.get(url)
    try:
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
    except Exception as e:
        print(f"Ocorreu um erro ao fazer login: {e}")

def agenda(driver):
    try:
        driver.execute_script("document.getElementById('cod_programa').value = arguments[0];", '236')
        driver.execute_script("document.getElementById('btn_programa').click();")
        time.sleep(2)
    except Exception as e:
        print(f"Ocorreu um erro ao selecionar o programa: {e}")

def clicar_botao(driver):
    try:
        driver.switch_to.frame('socframe')
        driver.execute_script("document.querySelector('#botoes > table > tbody > tr > td:nth-child(5) > a:nth-child(9) > img').click();")
        time.sleep(2)
    except Exception as e:
        print(f"Ocorreu um erro ao clicar no botão: {e}")

def aplicar_filtro(driver):
    try:
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
    except Exception as e:
        print(f"Ocorreu um erro ao aplicar o filtro: {e}")

def tela_chamada(driver):
    try:
        driver.execute_script("document.querySelector('#botoes > table > tbody > tr > td:nth-child(5) > a:nth-child(2) > img').click();")
    except Exception as e:
        print(f"Ocorreu um erro ao clicar no outro botão: {e}")

def abrir_ultimas_chamadas(driver):
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame('socframe')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#sim > i"))
        )
        driver.execute_script("document.querySelector('#sim > i').click();")
        pyautogui.press('F11')
    except Exception as e:
        print(f"Ocorreu um erro ao abrir as últimas chamadas: {e}")

def obter_timer(driver):
    try:
        # Se o timer estiver dentro de um iframe, mude para o contexto do iframe
        # driver.switch_to.frame('nome_ou_id_do_iframe')
        driver.switch_to.default_content()

        # Esperar o elemento ser visível
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="timerSessao"]'))
        )

        # Agora buscar o elemento no Xpath
        elemento = driver.find_element(By.XPATH, '//*[@id="timerSessao"]')
        valor_timer = elemento.text

        # Exibir o valor capturado
        print("Valor do timerSessao:", valor_timer)
        return valor_timer  # Retorna o valor do timer

    except Exception as e:
        print(f"Erro ao obter o timer: {e}")
        
def monitorar_timer(driver):
    while True:
        valor_timer = obter_timer(driver)
        if valor_timer:
            print(f"Valor do timerSessao: {valor_timer}")
            timer_int = int(valor_timer[3:])
            if timer_int > 0 and timer_int <= 10:
                print("Tempo expirando! Reiniciando o navegador...")
                driver.quit()  # Fecha o navegador
                #time.sleep(5)  # Aguarda 5 segundos antes de reiniciar
                main()  # Chama a função principal para reiniciar o processo
                break
            else:
                print("Aguardando 15 segundos para nova verificação...")
                time.sleep(300)
        else:
            print("Falha ao obter o timer. Tentando novamente em 1 minuto...")

def main():
    driver = configurar_driver()
    fazer_login(driver)
    agenda(driver)
    clicar_botao(driver)
    aplicar_filtro(driver)
    tela_chamada(driver)
    abrir_ultimas_chamadas(driver)
    obter_timer(driver)
    monitorar_timer(driver)

if __name__ == "__main__":
    main()
