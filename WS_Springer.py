import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd
import time

# Configuração do WebDriver
options = Options()
options.add_argument('window-size=1200,800')
options.add_argument('--ignore-certificate-errors')  # Ignorar erros de SSL

navegador = webdriver.Chrome(options=options)

# URL base para as páginas de jornais de Ciência da Computação
url_base = "https://link.springer.com/search?new-search=true&query=&sortBy=relevance&facet-discipline=%22Computer+Science%22&content-type=journal&page="
page_number = 1  

# Lista para armazenar os dados dos jornais
dados_jornais = []

# Loop para percorrer as páginas
while True:
    # Acessar a página atual
    navegador.get(url_base + str(page_number))
    print(f"Acessando página {page_number}...")

    # Aguarda a página carregar
    time.sleep(2)
    wait = WebDriverWait(navegador, 20)

    try:
        # Espera até que os jornais estejam presentes na página
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'app-card-open')))
        
        # Extrai o conteúdo da página
        page_content = navegador.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        
        # Encontrar todos os jornais na página
        jornais = soup.find_all('li', class_='app-card-open')
        
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
                
                # Acessar a página do jornal para extrair os updates
                navegador.get(link_jornal)
                time.sleep(2)

                # Extrair o conteúdo da página do jornal
                page_content_journal = navegador.page_source
                soup_journal = BeautifulSoup(page_content_journal, 'html.parser')
                
                # Extração de updates
                updates_section = soup_journal.find('ul', {'data-test': 'updates'})
                updates_data = []
                
                if updates_section:
                    # Encontrar todos os itens de atualização
                    updates = updates_section.find_all('li', class_='c-list-bullets')
                    keywords = ["call for papers", "special issue", "cfp"]

                    for update in updates:
                        title_element = update.find('a', class_='app-card-highlight__heading-link')
                        if title_element:
                            title = title_element.text.strip().lower()
                            if any(keyword in title for keyword in keywords):
                                # Extrair o título e o link da atualização
                                update_link = "https://link.springer.com" + title_element['href']
                                submission_deadline_tag = update.find('div', class_='app-card-highlight__text')
                                
                                # Verificar o prazo de submissão
                                if submission_deadline_tag:
                                    submission_text = submission_deadline_tag.text.strip()
                                    if 'Submission Deadline:' in submission_text or 'Submission deadline:' in submission_text:
                                        deadline_index = submission_text.lower().find('submission deadline:')
                                        submission_section = submission_text[deadline_index:].split(':', 1)[1].strip()

                                        # Remover "Guest Editors" se presente
                                        if 'Guest Editors:' in submission_section:
                                            submission_display = submission_section.split('Guest Editors:')[0].strip()
                                        else:
                                            submission_display = submission_section
                                    else:
                                        submission_display = "Nao ha prazo de submissao claramente definido"
                                else:
                                    submission_display = "Nao ha prazo de submissao"

                                updates_data.append({
                                    "Titulo": title_element.text.strip(),
                                    "Link": update_link,
                                    "Prazo de Submissao": submission_display
                                })

                dados_jornais.append({
                    "Nome do Jornal": nome_jornal,
                    "Link do Jornal": link_jornal,
                    "Updates": updates_data
                })

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
data = []
for jornal in dados_jornais:
    for update in jornal["Updates"]:
        data.append({
            "Nome do Jornal": jornal["Nome do Jornal"],
            "Link do Jornal": jornal["Link do Jornal"],
            "Titulo do Update": update["Titulo"],
            "Link do Update": update["Link"],
            "Prazo de Submissao": update["Prazo de Submissao"]
        })

df = pd.DataFrame(data, columns=['Nome do Jornal', 'Link do Jornal', 'Titulo do Update', 'Link do Update', 'Prazo de Submissao'])

# Salvar o DataFrame em um arquivo Excel
df.to_excel('WS_Springer.xlsx', index=False)

print("Dados extraídos e salvos em 'WS_Springer.xlsx'.")