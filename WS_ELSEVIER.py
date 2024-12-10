from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configurações do WebDriver
options = Options()
options.add_argument('--headless')  
options.add_argument('window-size=1200x600')

# Inicie o navegador
navegador = webdriver.Chrome(options=options)

# Acesse a página inicial
url = "https://www.sciencedirect.com/browse/calls-for-papers?subject=computer-science"
navegador.get(url)

# Espera até que o conteúdo seja carregado
WebDriverWait(navegador, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li.publication"))
)

# Extrair o conteúdo da página com Selenium
page_content = navegador.page_source

# Analisar o HTML com BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')

data = []

# Encontrar todas as seções de publicações
publications = soup.find_all('li', class_='publication')

for publication in publications:
    # Extrair o título da publicação
    title_element = publication.find('span', class_='anchor-text')
    title = title_element.text.strip() if title_element else "Título não encontrado"
    
    # Extrair o nome da revista
    journal_element = publication.find('p', class_='publication-text')
    journal = journal_element.text.strip().split('•')[0].strip() if journal_element else "Revista não encontrada"

    # Extrair a data de submissão
    deadline_element = publication.find_all('div', class_='text-s')
    submission_deadline = "Data não encontrada"
    
    for element in deadline_element:
        if 'Submission deadline:' in element.text:
            strong_tag = element.find('strong')
            if strong_tag:
                submission_deadline = strong_tag.text.strip()
                break

    if submission_deadline == "Data não encontrada":
        for element in deadline_element:
            if 'Submission' in element.text:  
                submission_text = element.text
                submission_start_index = submission_text.find('Submission')
                if submission_start_index != -1:
                    submission_deadline = submission_text[submission_start_index:].split(':')[-1].strip()
                    break 

    # Extrair o link
    link_element = publication.find('a', class_='anchor')
    link = "Link não encontrado"
    
    if link_element and 'href' in link_element.attrs:
        link = "https://www.sciencedirect.com" + link_element['href']
    
     # Acessar o link para extrair o resumo
    resumo = "Resumo não encontrado"
    if link != "Link não encontrado":
        try:
            navegador.get(link)
            time.sleep(2) 

            # Obter o conteúdo da página do link
            page_content = navegador.page_source
            soup_link = BeautifulSoup(page_content, 'html.parser')
            
            # Tentativa de extrair o resumo do contêiner padrão
            item_div = soup_link.find('div', class_='cfp-item')
            if item_div:
                resumo_text = []
                total_chars = 0
                max_chars = 500  # Limite de caracteres para o resumo

                for paragraph in item_div.find_all('p', recursive=True):
                    paragraph_text = paragraph.get_text(strip=True)
                    
                    # Excluir parágrafos indesejados
                    if not any(undesired in paragraph_text for undesired in ["Guest editors:", "Manuscript submission information", "Contact","Guest Editors:","Guest Editor:","GUEST EDITOR"]):
                        # Checa se o próximo parágrafo ultrapassará o limite de caracteres
                        if total_chars + len(paragraph_text) > max_chars:
                            break
                        
                        resumo_text.append(paragraph_text)
                        total_chars += len(paragraph_text)
                
                resumo = " ".join(resumo_text) if resumo_text else "Resumo não disponível"
            
            # Caso o contêiner padrão não contenha um resumo, buscar uma alternativa
            if resumo == "Resumo não disponível":
                alternative_paragraph = soup_link.find('p')  # Buscar o primeiro parágrafo da página como alternativa
                if alternative_paragraph:
                    resumo = alternative_paragraph.get_text(strip=True)[:500]  

            if resumo == "Resumo não disponível":
                # Tenta buscar o resumo a partir de um outro <div> específico ou qualquer outro conteúdo de destaque
                content_div = soup_link.find('div', id='updates-content-body')  
                if content_div:
                    paragraph = content_div.find('p')  # Seleciona o primeiro parágrafo dentro do div
                    if paragraph:
                        resumo = paragraph.text.strip()[:500]  

        except Exception as e:
            print(f"Erro ao acessar o link {link}: {e}")
            resumo = "Erro ao acessar o link"
    
    # Adicionar os dados à lista
    data.append([title, journal, submission_deadline, link, resumo])

# Criar um DataFrame e salvar em Excel
df = pd.DataFrame(data, columns=['Título', 'Revista', 'Submission Deadline', 'Link', 'Resumo'])
output_file_path = 'WS_ELSEVIER2.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Os resultados foram salvos na planilha: {output_file_path}")

# Fechar o navegador
navegador.quit()
