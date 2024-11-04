from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Configurações do WebDriver
options = Options()
#options.add_argument('--headless')
options.add_argument('window-size=1200x600')

# Inicie o navegador
navegador = webdriver.Chrome(options=options)

# Acesse a página desejada
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

# Lista para armazenar os dados
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
    resumo = journal_element.text.strip() if journal_element else "Resumo não encontrado"

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
                # Extrair o texto a partir de "Submission"
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
    
    # Adicionar os dados à lista
    data.append([title, journal, submission_deadline, link, resumo])

# Criar um DataFrame e salvar em Excel
df = pd.DataFrame(data, columns=['Título', 'Revista', 'Submission Deadline', 'Link', 'Resumo'])
output_file_path = 'WS_ELSEVIER.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Os resultados foram salvos na planilha: {output_file_path}")

# Fechar o navegador
navegador.quit()
