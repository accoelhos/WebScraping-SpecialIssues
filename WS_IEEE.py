# ROTINA DE BUSCA PARA IEEE

import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "https://www.computer.org/publications/author-resources/calls-for-papers"

response = requests.get(url)

if response.status_code == 200:
   
    soup = BeautifulSoup(response.text, 'html.parser')
    call_for_papers = soup.find_all('div', class_='callForPaperPostContainer')
    
    data = []
    # Iterando por cada chamada para artigos encontrada
    for call in call_for_papers:
        # Extraindo o tipo de chamada 
        tipo = call.get('data-callforpaper-type', 'No type')

        # Extraindo o título e o link
        titulo_elemento = call.find('div', class_='callForPaperPostTitle')
        titulo = titulo_elemento.get_text(strip=True) if titulo_elemento else 'No title'
        link_elemento = titulo_elemento.find('a') if titulo_elemento else None
        link = link_elemento['href'] if link_elemento else 'No link'
        
        # Extraindo o resumo
        resumo_elemento = call.find('div', class_='callForPaperPostSummary')
        resumo = resumo_elemento.get_text(strip=True) if resumo_elemento else 'No summary'
        
        # Extraindo a data de submissão 
        deadline_elemento = call.find('span', class_='callForPaperPostNominationDeadline')
        deadline = deadline_elemento.get_text(strip=True) if deadline_elemento else 'No deadline'
        
        data.append([tipo,titulo,link, resumo, deadline])
        print(f"Tipo: {tipo}\nTítulo: {titulo}\nLink: {link}\nResumo: {resumo}\nDeadline: {deadline}\n\n")
    df = pd.DataFrame(data, columns=['Tipo', 'Título', 'Link', 'Resumo', 'Deadline'])

    output_file_path= 'WS_IEEE.xlsx'
    df.to_excel(output_file_path, index= False)

    print(f"Os resultados foram salvos na planilha: {output_file_path}")
else:
    print("Não foi possível abrir a página.")
