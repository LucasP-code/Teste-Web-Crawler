import csv
from requests import get
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import os

def spray_link():
    links = []
    key_words = ['pulverizador', 'costal', 'manual']

    page_mercado_livre = get("https://lista.mercadolivre.com.br/pulverizador-costal-manual#D[A:pulverizador%20costal%20manual]")

    soup_mercado_livre = BeautifulSoup(page_mercado_livre.content, 'html.parser')

    spray = soup_mercado_livre.find('ol', {'class': 'ui-search-layout ui-search-layout--grid'})
    spray_list = spray.find_all('li', {'class': 'ui-search-layout__item'})

    for i in spray_list:
        spray_name = i.find('h2', {'class': 'poly-box poly-component__title'}).get_text()

        if all(word in spray_name.lower() for word in key_words):    
            spray_link = i.find('a')
            links.append(spray_link.get('href'))

    return links

def spray_Info(links):
    spray_info = []
    for pulv in links:
        spray_page = get(pulv)
        spray_soup = BeautifulSoup(spray_page.content, 'html.parser')

        spray_name = spray_soup.find('h1', {'class': 'ui-pdp-title'}).get_text()

        spray_price = spray_soup.find('div', {'class': 'ui-pdp-price__second-line'})

        spray_value = spray_price.find('span', {'class': 'andes-money-amount__fraction'}).get_text()

        spray_brand_model = spray_soup.find_all('tr', {'class': 'andes-table__row ui-vpp-striped-specs__row'})

        spray_brand = ""
        spray_model = ""
        for i in spray_brand_model:
            if i.find('th', string='Marca'):
                spray_brand = i.find('td').get_text(strip=True)
            if i.find('th', string='Modelo'):
                spray_model = i.find('td').get_text(strip=True)
        
        if spray_brand == "" or spray_model == "":
            continue

        spray_info.append([spray_name, spray_value, spray_brand, spray_model])

    return spray_info

def save_file(info):
    if not os.path.exists('pulverizadores.csv'):
        with open('pulverizadores.csv', 'w', encoding="utf-8", newline='') as file:
            writeCSV = csv.writer(file)
            writeCSV.writerow(['Nome', 'Preco', 'Marca', 'Modelo'])
            for i in info:
                writeCSV.writerow(i)

def spray_median():
    data = pd.read_csv('pulverizadores.csv')

    group = data.groupby(['Marca', 'Modelo']).size().reset_index(name='Contagem')
    spray_brand_median = group.groupby('Marca')['Contagem'].median()
    spray_brand_model = group.groupby(['Marca', 'Modelo']).agg({'Contagem': 'median'}).reset_index()
    
    spray_brand_model.to_csv('mediana_pulverizadores.csv', index=False)

    plt.figure(figsize=(10, 5))
    spray_brand_median.plot(kind='bar', color='orange')
    plt.xlabel('Marca')
    plt.ylabel('Mediana dos Modelos')
    plt.title('Mediana de Pulverizadores por Marca/Modelo')
    plt.show()

def main():
    busca_pulverizadores = spray_link()
    info = spray_Info(busca_pulverizadores)
    print(info)
    save_file(info)
    spray_median()

if __name__ == "__main__":
    main()
