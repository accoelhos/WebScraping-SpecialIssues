import requests
from bs4 import BeautifulSoup

# Função para ler URLs de um arquivo
def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls

urls_file_path = 'urls_springer.txt'
urls = read_urls_from_file(urls_file_path)

# Verificar se os URLs foram lidos corretamente
if not urls:
    print("Nao foram encontradas URL nesse arquivo.")
else:
    print(f"Encontradas {len(urls)} URLs para busca.")

# Processar cada URL do arquivo
for url in urls:
    print("\n")
    print("=====================================================================================")
    print(f"\nBuscando URL: {url}")

    # solicitação HTTP para obter o conteúdo da página
    response = requests.get(url)

    # Verificar se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Analisar o conteúdo da página com BeautifulSoup
        site = BeautifulSoup(response.text, 'html.parser')

        # Obter o nome do journal
        journal_title_element = site.find('h1', class_='app-journal-masthead__title')
        if journal_title_element:
            journal_title = journal_title_element.text.strip()
            print(f"Journal: {journal_title}")
        else:
            # encontrar o elemento usando a classe CSS diretamente
            journal_title_element = site.select_one('.app-journal-masthead__title')
            if journal_title_element:
                journal_title = journal_title_element.text.strip()
                print(f"Journal: {journal_title}")
            else:
                journal_title = "Nome do jornal nao encontrado"
                print(f"Journal: {journal_title}")

        # seção de updates
        updates_section = site.find('ul', {'data-test': 'updates'})

        if updates_section:
            # Encontrar todos os itens da lista dentro desta seção
            updates = updates_section.find_all('li', class_='c-list-bullets')

            # Palavras-chave para identificar chamadas
            keywords = ["call for papers", "special issue", "cfp"]

            # Verificar cada atualização para as palavras-chave nos títulos
            found_updates = False
            for update in updates:
                title_element = update.find('a', class_='app-card-highlight__heading-link')
                if title_element:
                    title = title_element.text.strip().lower()
                    if any(keyword in title for keyword in keywords):
                        # Extrair e imprimir as infos
                        link = "https://link.springer.com" + title_element['href']
                        print(f"Titulo: {title_element.text.strip()}\nLink: {link}")

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

                                print(f"Submission Deadline: {submission_display}")
                            else:
                                print("Nao ha prazo de submissao claramente definido")
                        else:
                            print("Nao ha prazo de submissao")
                        print("\n")
                        found_updates = True

            if not found_updates:
                print("Nao ha Special Issues")
        else:
            print("Nao ha updates")
    else:
        print(f"Nao foi possível abrir essa pagina: {url}")
