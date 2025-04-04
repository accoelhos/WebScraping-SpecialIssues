from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuração do WebDriver
options = Options()
options.add_argument('--headless')  # Executar sem abrir o navegador
options.add_argument('window-size=1200x600')

# Inicializa o navegador
navegador = webdriver.Chrome(options=options)

# Acesse a página inicial da Wiley
url = "https://onlinelibrary.wiley.com/action/doSearch?AllField=issue&ConceptID=68&content=collections&startPage={}&target=collections&pageSize=20000"

navegador.get(url)

# Espera até que o conteúdo seja carregado
WebDriverWait(navegador, 100).until(
    EC.presence_of_element_located((By.CLASS_NAME, "search__item"))
)

# Extrair o conteúdo da página com Selenium
page_content = navegador.page_source

# Analisar o HTML com BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')

# Lista para armazenar os dados
data = []

# Encontrar todas as seções das publicações
publications = soup.find_all('li', class_='search__item')

for publication in publications:
    time.sleep(2)  # Pequena pausa para evitar bloqueios

    # Extrair o nome correto da revista usando o link secundário
    journal = "Revista não encontrada"
    journal_link_element = publication.find_all('a', href=True)
    if len(journal_link_element) > 1:  # Garante que pega o segundo link (nome da revista)
        journal = journal_link_element[1].text.strip()

    # Extrair o título da publicação
    title_element = publication.find('h3', class_='meta__title')
    title = title_element.text.strip() if title_element else "Título não encontrado"

    # Extrair o link da publicação
    link_element = title_element.find('a', href=True) if title_element else None
    link = "Link não encontrado"
    if link_element:
        link = "https://onlinelibrary.wiley.com" + link_element['href']

    # Extrair a data da publicação
    date_element = publication.find('p', class_='volume-issue')
    publication_date = date_element.text.strip() if date_element else "Data não encontrada"

    

    

    # Adicionar os dados à lista
    data.append([journal, title,link, publication_date])

# Criar um DataFrame e salvar em Excel
df = pd.DataFrame(data, columns=['Revista', 'Titulo', 'Link', 'detalhes'])
output_file_path = 'WS_WILEY.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Os resultados foram salvos na planilha: {output_file_path}")

# Fechar o navegador
navegador.quit()