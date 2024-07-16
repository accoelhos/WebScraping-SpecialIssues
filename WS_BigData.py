#Rotina de busca de Special Issues para o Journal of Big Data
import requests
from bs4 import BeautifulSoup


url = "https://journalofbigdata.springeropen.com"

response = requests.get(url)

if response.status_code == 200:

    site = BeautifulSoup(response.text, 'html.parser')
    special_issues_section = site.find('div', {'id': 'open+special+issues'})

    if special_issues_section:
        
        paragraphs = special_issues_section.find_all('p')

        
        for paragraph in paragraphs:
            
            title_element = paragraph.find('a', class_='is-external')
            if title_element:
                
                titulo = title_element.text.strip()
                link = title_element['href']

                
                deadline_element = paragraph.find('em')
                deadline = deadline_element.text.strip() if deadline_element else 'No deadline'

                print(f"Title: {titulo}\nLink: {link}\n{deadline}\n\n")
    else:
        print("Nao ha special issues")
else:
    print("Nao foi possivel abrir a pagina")
