import requests
from bs4 import BeautifulSoup
import pandas as pd

# Função para ler URLs de um arquivo
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

urls_file_path = 'urls_springer.txt'
urls = read_urls_from_file(urls_file_path)

# Verificar se os URLs foram lidos corretamente
if not urls:
    print("Não foram encontradas URLs nesse arquivo.")
else:
    print(f"Encontradas {len(urls)} URLs para busca.")

# Lista para armazenar os dados
data = []

# Processar cada URL do arquivo
for url in urls:
    print("\n")
    print("=====================================================================================")
    print(f"\nBuscando URL: {url}")

    # Solicitação HTTP para obter o conteúdo da página
    response = requests.get(url)

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Analisar o conteúdo da página com BeautifulSoup
        site = BeautifulSoup(response.text, 'html.parser')

        # Obter o nome do journal
        journal_title_element = site.find('h1', class_='app-journal-masthead__title')
        if journal_title_element:
            journal_title = journal_title_element.text.strip()
        else:
            # Encontrar o elemento usando a classe CSS diretamente
            journal_title_element = site.select_one('.app-journal-masthead__title')
            if journal_title_element:
                journal_title = journal_title_element.text.strip()
            else:
                journal_title = "Nome do journal não encontrado"

        # Seção de updates
        updates_section = site.find('ul', {'data-test': 'updates'})

        if updates_section:
            # Encontrar todos os itens da lista dentro desta seção
            updates = updates_section.find_all('li', class_='c-list-bullets')

            # Palavras-chave para identificar chamadas
            keywords = ["call for papers", "special issue", "cfp"]

            # Verificar cada atualização para as palavras-chave nos títulos
            for update in updates:
                title_element = update.find('a', class_='app-card-highlight__heading-link')
                if title_element:
                    title = title_element.text.strip().lower()
                    if any(keyword in title for keyword in keywords):
                        # Extrair e armazenar as infos
                        link = "https://link.springer.com" + title_element['href']
                        special_issue_title = title_element.text.strip()

                        # Verificar prazo de submissão
                        submission_deadline_tag = update.find('div', class_='app-card-highlight__text')
                        if submission_deadline_tag:
                            submission_text = submission_deadline_tag.text.strip()
                            if 'Submission Deadline:' in submission_text or 'Submission deadline:' in submission_text:
                                # Encontrar e extrair a data de submissão
                                deadline_index = submission_text.lower().find('submission deadline:')
                                submission_section = submission_text[deadline_index:].split(':', 1)[1].strip()

                                # Remover "Guest Editors" se estiver presente
                                if 'Guest Editors:' in submission_section:
                                    submission_display = submission_section.split('Guest Editors:')[0].strip()
                                else:
                                    submission_display = submission_section

                                submission_deadline = submission_display
                            else:
                                submission_deadline = "Não há prazo de submissão claramente definido"
                        else:
                            submission_deadline = "Não há prazo de submissão"

                        data.append([journal_title, special_issue_title, link, submission_deadline])

# Criar um DataFrame do pandas com os dados
df = pd.DataFrame(data, columns=['Journal', 'Special Issue Title', 'Link', 'Submission Deadline'])

# Salvar o DataFrame em uma planilha Excel
output_file_path = 'special_issues.xlsx'
df.to_excel(output_file_path, index=False)

print(f"Os resultados foram salvos na planilha: {output_file_path}")
