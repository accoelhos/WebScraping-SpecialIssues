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
options.add_argument('--ignore-certificate-errors')

navegador = webdriver.Chrome(options=options)

# URL base para as páginas
url_base = "https://link.springer.com/search?new-search=true&query=&sortBy=relevance&facet-discipline=%22Computer+Science%22&content-type=journal&page="
page_number = 1

# Lista e conjunto para armazenar dados dos jornais e evitar duplicatas
dados_jornais = []
links_processados = set()

# Palavras-chave para filtro
keywords = ["call for papers", "special issue", "cfp"]

# Limite de caracteres do resumo
RESUMO_CHAR_LIMIT = 500

# Loop para percorrer as páginas
while True:
    navegador.get(url_base + str(page_number))
    print(f"Acessando página {page_number}...")
    
    sleep(2)
    wait = WebDriverWait(navegador, 20)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'app-card-open')))
        
        page_content = navegador.page_source
        soup = BeautifulSoup(page_content, 'html.parser')
        jornais = soup.find_all('li', class_='app-card-open')
        
        if not jornais:
            print("Nenhum artigo encontrado na página. Fim da navegação.")
            break

        for jornal in jornais:
            try:
                nome_jornal_element = jornal.find('h3', class_='app-card-open__heading')
                nome_jornal = nome_jornal_element.text.strip() if nome_jornal_element else "Nome não encontrado"
                
                link_jornal_element = nome_jornal_element.find('a')
                link_jornal = link_jornal_element['href'] if link_jornal_element else "Link não encontrado"

                if not link_jornal.startswith('https'):
                    link_jornal = "https://link.springer.com" + link_jornal
                
                navegador.get(link_jornal)
                sleep(2)

                try:
                    view_updates_button = navegador.find_element(By.XPATH, "//a[@data-test='view-all-updates-button']")
                    navegador.execute_script("arguments[0].click();", view_updates_button)
                    sleep(2)

                    page_content = navegador.page_source
                    soup_updates = BeautifulSoup(page_content, 'html.parser')
                    updates = soup_updates.find_all('article', class_='app-card-highlight')

                    for update in updates:
                        resumo = "Resumo não disponível"  # Sempre reiniciar o resumo para cada update
                        
                        link_update_element = update.find('a', class_='app-card-highlight__heading-link')
                        titulo_update = link_update_element.text.strip() if link_update_element else "Título não encontrado"
                        
                        if any(keyword in titulo_update.lower() for keyword in keywords):
                            link_update = "https://link.springer.com" + link_update_element['href'] if link_update_element else "Link não encontrado"

                            if link_update in links_processados:
                                print(f"Update já processado: {link_update}")
                                continue

                            links_processados.add(link_update)

                            # Verificar o prazo de submissão
                            submission_deadline_tag = update.find('div', class_='app-card-highlight__text')
                            prazo_submissao = "Prazo não claramente definido"  # Valor padrão

                            if submission_deadline_tag:
                                submission_text = submission_deadline_tag.text.strip()
                                if any(term in submission_text.lower() for term in ['submission deadline:', 'submissions due:']):
                                    deadline_index = min(
                                        submission_text.lower().find(term)
                                        for term in ['submission deadline:', 'submissions due:']
                                        if submission_text.lower().find(term) != -1
                                    )
                                    submission_section = submission_text[deadline_index:].split(':', 1)[1].strip()

                                    if 'Guest Editors:' in submission_section:
                                        prazo_submissao = submission_section.split('Guest Editors:')[0].strip()
                                    else:
                                        prazo_submissao = submission_section
                                else:
                                    prazo_submissao = "Prazo não encontrado na descrição inicial"

                            # Se o prazo ainda não foi encontrado, acessar o link do update e procurar novamente
                            if prazo_submissao == "Prazo não claramente definido":
                                navegador.get(link_update)
                                sleep(2)
                                update_page_content = navegador.page_source
                                soup_update_page = BeautifulSoup(update_page_content, 'html.parser')

                                # Procurar pelo prazo na página do update
                                submission_deadline_tag = soup_update_page.find('div', class_='app-page-content')
                                if submission_deadline_tag:
                                    submission_text = submission_deadline_tag.text.strip()
                                    if any(term in submission_text.lower() for term in ['submission deadline:', 'submissions due:', 'submission system closes:']):
                                        deadline_index = min(
                                            submission_text.lower().find(term)
                                            for term in ['submission deadline:', 'submissions due:', 'submission system closes:']
                                            if submission_text.lower().find(term) != -1
                                        )
                                        submission_section = submission_text[deadline_index:].split(':', 1)[1].strip()

                                        if 'Guest Editors:' in submission_section:
                                            prazo_submissao = submission_section.split('Guest Editors:')[0].strip()
                                        else:
                                            prazo_submissao = submission_section
                                    else:
                                        prazo_submissao = "Prazo não encontrado no link do update"

                            # Extração do resumo
                            try:
                                navegador.get(link_update)
                                wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'c-list-bullets')))

                                update_page_content = navegador.page_source
                                soup_update_page = BeautifulSoup(update_page_content, 'html.parser')

                                resumo_tag = soup_update_page.find('div', class_='c-list-bullets app-content-page app-coremedia-content-page')
                                if resumo_tag:
                                    paragraphs = resumo_tag.find_all('p')
                                    resumo = " ".join([p.text.strip() for p in paragraphs])
                                    resumo = resumo[:RESUMO_CHAR_LIMIT] + "..." if len(resumo) > RESUMO_CHAR_LIMIT else resumo

                            except Exception as e:
                                print(f"Erro ao processar resumo ou prazo para update {titulo_update}: {str(e)}")

                            # Adicionar o registro após todos os campos serem processados
                            dados_jornais.append([nome_jornal, link_jornal, titulo_update, link_update, prazo_submissao, resumo])

                except NoSuchElementException:
                    print(f"O jornal '{nome_jornal}' não possui um botão 'View all updates'. Seguindo para o próximo.")

            except Exception as e:
                print(f"Erro ao processar o jornal: {nome_jornal} - Erro: {str(e)}")

        page_number += 1

    except TimeoutException:
        print("Tempo esgotado para carregar a página, encerrando o loop...")
        break

navegador.quit()

df = pd.DataFrame(dados_jornais, columns=['Nome do Jornal', 'Link do Jornal', 'Título do Update', 'Link do Update', 'Prazo de Submissão', 'Resumo'])
df.to_excel('WS_Springer.xlsx', index=False)

print("Dados extraídos e salvos em 'WS_Springer.xlsx'.")
