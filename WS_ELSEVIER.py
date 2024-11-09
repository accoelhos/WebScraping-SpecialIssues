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
# options.add_argument('--headless')  # Execute sem abrir o navegador
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
    
    # Acessar o link para extrair o conteúdo do primeiro <p> com estilo
    resumo = "Resumo não encontrado"
    if link != "Link não encontrado":
        try:
            navegador.get(link)
            time.sleep(2)  # Pausa para o conteúdo carregar

            # Obter o conteúdo da página do link
            page_content = navegador.page_source
            soup_link = BeautifulSoup(page_content, 'html.parser')
            
            # Procurar o primeiro <p> que contenha o atributo style
            first_p_with_style = soup_link.find('p', style=False)
            
            # Extrair o texto até o primeiro ponto final
            if first_p_with_style:
                full_text = first_p_with_style.text.strip()
                resumo = full_text.split('.')[0] + "." if '.' in full_text else full_text
            else:
                resumo = "Resumo não disponível"
        
        except Exception as e:
            print(f"Erro ao acessar o link {link}: {e}")
            resumo = "Erro ao acessar o link"
    
    # Adicionar os dados à lista
    data.append([title, journal, submission_deadline, link, resumo])

# Criar um DataFrame e salvar em Excel
df = pd.DataFrame(data, columns=['Título', 'Revista', 'Submission Deadline', 'Link', 'Resumo'])
output_file_path = 'WS_ELSEVIER.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Os resultados foram salvos na planilha: {output_file_path}")

# Fechar o navegador
navegador.quit()
