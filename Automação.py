from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Inicializa o navegador
driver = webdriver.Chrome()  # ou webdriver.Firefox() para Firefox

try:
    # Acessa a página inicial
    driver.get("https://link.springer.com/search?new-search=true&query=&sortBy=relevance&facet-discipline=%22Computer+Science%22&content-type=journal")
    
    # Cria uma instância de WebDriverWait
    wait = WebDriverWait(driver, 10)

    while True:
        # Aguarda até que todos os links de revistas estejam carregados
        wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "app-card-open__link"))
        )

        # Encontra todos os elementos de link que correspondem ao seletor
        links = driver.find_elements(By.CLASS_NAME, "app-card-open__link")

        # Abre um arquivo para gravar os links
        with open('links.txt', 'w') as file: 
            for link in links:
                # Extraia o href e escreva no arquivo
                file.write(link.get_attribute('href') + '\n')

        try:
            # Espera até que o botão "Next" esteja clicável
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.eds-c-pagination__link[rel='next']")))
            
            # Desloca a janela até o botão "Next"
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)  # Espera um pouco para garantir que o botão está visível

            # Tenta clicar no botão usando JavaScript
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)  # Aumenta o tempo de espera para carregar a próxima página

        except Exception as e:
            print("Erro ao tentar clicar no botão de próxima página:", str(e))
            break  # Sai do loop se não houver mais páginas

finally:
    # Feche o navegador
    driver.quit()
