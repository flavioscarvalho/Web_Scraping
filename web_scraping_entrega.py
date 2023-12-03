# Bibliotecas
import requests  # Biblioteca para fazer requisições HTTP
import time  # Biblioteca para medir o tempo de execução
import csv  # Biblioteca para manipulação de arquivos CSV
import random  # Biblioteca para gerar números aleatórios
import concurrent.futures  # Biblioteca para execução concorrente de tarefas

from bs4 import BeautifulSoup  # Biblioteca para fazer scraping de HTML

# Configuração do cabeçalho para simular um navegador (User-Agent)
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

# Número máximo de threads a serem usadas
MAX_THREADS = 10

# Função para extrair detalhes de um filme dado um link
def extract_movie_details(movie_link, title):
    # Adiciona um pequeno atraso aleatório para evitar bloqueios por parte do servidor
    time.sleep(random.uniform(0, 0.2))

    # Faz uma requisição HTTP para obter o conteúdo da página do filme
    response = BeautifulSoup(requests.get(movie_link, headers=headers).content, 'html.parser')
    movie_soup = response

    # Verifica se a página foi obtida com sucesso
    if movie_soup is not None:
        date = None
        censura = None
        duracao = None

        # Extrai informações sobre o filme da seção 'title_wrapper'
        ul_data_movie = movie_soup.find('ul', { 'class': 'ipc-inline-list ipc-inline-list--show-dividers sc-7f1a92f5-4 kIoyyw baseAlt' })
        contador = 0
        for li in ul_data_movie:
            if contador == 0:
                date = li.a.text
            elif contador == 1:
                censura = li.a.text
            elif contador == 2:
                duracao = li.text
            contador += 1

        # Extrai o texto do enredo do filme, se disponível
        plot_text = movie_soup.find('span', { 'class': 'sc-466bb6c-0 hlbAws'}).text

        #Extrai a avaliação
        rating = movie_soup.findAll('div', { 'class': 'sc-bde20123-2 cdQqzc'})[0].text

        # Escreve os detalhes do filme em um arquivo CSV
        with open('movies.csv', mode='a') as file:
            movie_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if all([title, date, rating, plot_text]):  # Verifica se todas as informações necessárias estão presentes
                print(title, date, rating, plot_text)  # Exibe os detalhes do filme no console
                movie_writer.writerow([title, date, rating, plot_text])  # Escreve os detalhes do filme no arquivo CSV

# Função para extrair links de filmes de uma página
def extract_movies(soup):
    # Encontra a tabela de filmes na página
    movie_table = soup.findAll('div', { 'class': 'ipc-poster ipc-poster--base ipc-poster--dynamic-width ipc-sub-grid-item ipc-sub-grid-item--span-2'})
    movie_titles = []
    movie_links = []
    for row in movie_table:
        nome = str(row.a['aria-label']).replace("View title page for ", "")
        link = 'https://imdb.com' + str(row.a['href'])
        movie_titles.append(nome)
        movie_links.append(link)

    # Determina o número de threads a serem usadas, no máximo MAX_THREADS
    threads = min(MAX_THREADS, len(movie_links))

    # Usa threads para extrair detalhes de filmes de forma concorrente
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        executor.map(extract_movie_details, movie_links, movie_titles)

# Função principal
def main():
    start_time = time.time()  # Marca o tempo de início da execução

    # URL da página dos 100 filmes mais populares no IMDb
    popular_movies_url = 'https://www.imdb.com/chart/moviemeter/?ref_=nv_mv_mpm'
    # Faz uma requisição HTTP para obter o conteúdo da página
    response = requests.get(popular_movies_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')  # Cria um objeto BeautifulSoup para fazer scraping do HTML

    extract_movies(soup)  # Chama a função para extrair detalhes dos filmes

    end_time = time.time()  # Marca o tempo de término da execução
    print('Total time taken: ', end_time - start_time)  # Exibe o tempo total de execução

# Verifica se o script está sendo executado diretamente
if __name__ == '__main__':
    main()  # Chama a função principal se o script estiver sendo executado diretamente

