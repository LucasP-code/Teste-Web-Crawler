import csv
from requests import *
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import pandas as pd
import os

def Links_Pulverizadores():
    links = []
    palavras_chave = ['pulverizador', 'costal', 'manual']

    pagina_mercado_livre = get("https://lista.mercadolivre.com.br/pulverizador-costal-manual#D[A:pulverizador%20costal%20manual]")

    sopa_mercado_livre = BeautifulSoup(pagina_mercado_livre.content, 'html.parser')

    pulverizadores = sopa_mercado_livre.find('ol', {'class': 'ui-search-layout ui-search-layout--grid'})
    lista_pulverizadores = pulverizadores.find_all('li', {'class': 'ui-search-layout__item'})

    for i in lista_pulverizadores:
        nome_pulverizadores = i.find('h2', {'class': 'poly-box poly-component__title'}).get_text()

        if all(palavra in nome_pulverizadores.lower() for palavra in palavras_chave):    
            link_pulverizador = i.find('a')
            links.append(link_pulverizador.get('href'))

    return links

def Info_Pulverizadores(links):
    info_pulverizadores = []
    for pulv in links:
        pagina_pulv = get(pulv)
        sopa_pulv = BeautifulSoup(pagina_pulv.content, 'html.parser')

        nome_pulverizador = sopa_pulv.find('h1', {'class': 'ui-pdp-title'}).get_text()

        preco_pulverizador = sopa_pulv.find('div', {'class': 'ui-pdp-price__second-line'})

        valor_pulverizador = preco_pulverizador.find('span', {'class': 'andes-money-amount__fraction'}).get_text()

        marca_modelo_pulverizador = sopa_pulv.find_all('tr', {'class': 'andes-table__row ui-vpp-striped-specs__row'})

        marca_pulverizador = ""
        modelo_pulverizador = ""
        for i in marca_modelo_pulverizador:
            if i.find('th', string='Marca'):
                marca_pulverizador = i.find('td').get_text(strip=True)
                #print(marca_pulverizador)
            if i.find('th', string='Modelo'):
                modelo_pulverizador = i.find('td').get_text(strip=True)
                #print(modelo_pulverizador)
        
        if marca_pulverizador == "" or modelo_pulverizador == "":
            continue

        info_pulverizadores.append([nome_pulverizador, valor_pulverizador, marca_pulverizador, modelo_pulverizador])

    return info_pulverizadores

def Salvar_Arquivo(informacoes):
    if not os.path.exists('pulverizadores.csv'):
        with open('pulverizadores.csv', 'w', encoding="utf-8", newline='') as arquivo:
            escreverCSV = csv.writer(arquivo)
            escreverCSV.writerow(['Nome', 'Preco', 'Marca', 'Modelo'])
            for i in informacoes:
                escreverCSV.writerow(i)

def Mediana_Pulverizadores():
    dados = pd.read_csv('pulverizadores.csv')

    agrupamento = dados.groupby(['Marca', 'Modelo']).size().reset_index(name='Contagem')
    marca_medianas_pulverizadores = agrupamento.groupby('Marca')['Contagem'].median()
    marca_modelo_pulverizadores = agrupamento.groupby(['Marca', 'Modelo']).agg({'Contagem': 'median'}).reset_index()
    
    marca_modelo_pulverizadores.to_csv('mediana_pulverizadores.csv', index=False)

    plt.figure(figsize=(10, 5))
    marca_medianas_pulverizadores.plot(kind='bar', color='orange')
    plt.xlabel('Marca')
    plt.ylabel('Mediana dos Modelos')
    plt.title('Mediana de Pulverizadores por Marca/Modelo')
    plt.show()

busca_pulverizadores = Links_Pulverizadores()
informacoes = Info_Pulverizadores(busca_pulverizadores)
print(informacoes)
Salvar_Arquivo(informacoes)
Mediana_Pulverizadores()
