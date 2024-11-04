from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd

# Configuração do WebDriver
options = Options()
options.add_argument('window-size=1200,800')
options.add_argument('--ignore-certificate-errors')  # Ignorar erros de SSL

navegador = webdriver.Chrome(options=options)

# URL base para as páginas
url_base = "https://link.springer.com/search?new-search=true&query=&sortBy=relevance&facet-discipline=%22Computer+Science%22&content-type=journal&page="
page_number = 1  # Número inicial da página

# Lista para armazenar os dados dos jornais e updates
dados_jornais = []

# Loop para percorrer as páginas
while True:
    # Acessar a página atual
    navegador.get(url_base + str(page_number))
    print(f"Acessando página {page_number}...")
    
    # Aguarda a página carregar
    sleep(2)
    wait = WebDriverWait(navegador, 20)

    try:
        # Espera até que os jornais estejam presentes na página
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'app-card-open')))
        
        # Extrai o conteúdo da página
        page_content = navegador.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Encontrar todos os jornais na página
        jornais = soup.find_all('li', class_='app-card-open')
        
        # Se não houver jornais na página, fim da navegação
        if not jornais:
            print("Nenhum artigo encontrado na página. Fim da navegação.")
            break

        # Iterar por cada jornal encontrado
        for jornal in jornais:
            try:
                # Extrair o nome do jornal
                nome_jornal_element = jornal.find('h3', class_='app-card-open__heading')
                nome_jornal = nome_jornal_element.text.strip() if nome_jornal_element else "Nome não encontrado"
                
                # Extrair o link do jornal
                link_jornal_element = nome_jornal_element.find('a')
                link_jornal = link_jornal_element['href'] if link_jornal_element else "Link não encontrado"

                # Completar o link (caso necessário)
                if not link_jornal.startswith('https'):
                    link_jornal = "https://link.springer.com" + link_jornal
                
                # Acessar o link do jornal
                navegador.get(link_jornal)
                sleep(2)

                # Tentar clicar no botão "View all updates"
                try:
                    view_updates_button = navegador.find_element(By.XPATH, "//a[@data-test='view-all-updates-button']")
                    navegador.execute_script("arguments[0].click();", view_updates_button)
                    sleep(2)

                    # Extrair o conteúdo da página de updates
                    page_content = navegador.page_source
                    soup_updates = BeautifulSoup(page_content, 'html.parser')

                    # Encontrar todos os updates
                    updates = soup_updates.find_all('article', class_='app-card-highlight')

                    # Iterar pelos updates
                    for update in updates:
                        link_update_element = update.find('a', class_='app-card-highlight__heading-link')
                        link_update = "https://link.springer.com" + link_update_element['href'] if link_update_element else "Link não encontrado"

                        titulo_update = link_update_element.text.strip() if link_update_element else "Título não encontrado"
                        
                        # Acessar o update para buscar o Special issue type (h1 tag)
                        navegador.get(link_update)
                        sleep(2)

                        page_content_update = navegador.page_source
                        soup_detail = BeautifulSoup(page_content_update, 'html.parser')
                        special_issue_type_element = soup_detail.find('h1', class_='u-h2 u-mb-48')
                        special_issue_type = special_issue_type_element.text.strip() if special_issue_type_element else "Special issue type não encontrado"

                        # Adicionar os dados à lista
                        dados_jornais.append([nome_jornal, link_jornal, titulo_update, link_update, special_issue_type])
                
                except NoSuchElementException:
                    print(f"O jornal '{nome_jornal}' não possui um botão 'View all updates'. Seguindo para o próximo.")

            except Exception as e:
                print(f"Erro ao processar o jornal: {nome_jornal} - Erro: {str(e)}")

        # Incrementar o número da página para acessar a próxima página
        page_number += 1
    
    except TimeoutException:
        print("Tempo esgotado para carregar a página, encerrando o loop...")
        break

# Fechar o navegador
navegador.quit()

# Converter os dados para um DataFrame do Pandas
df = pd.DataFrame(dados_jornais, columns=['Nome do Jornal', 'Link do Jornal', 'Título do Update', 'Link do Update', 'Special Issue Type'])

# Salvar o DataFrame em um arquivo Excel
df.to_excel('jornais_updates.xlsx', index=False)

print("Dados extraídos e salvos em 'jornais_updates.xlsx'.")
