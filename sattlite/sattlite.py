from bs4 import BeautifulSoup
import requests
import csv
import sqlite3

def parse_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('div', class_='news-content')
        data = []
        for i, a in enumerate(articles):
            date = a.find('span', class_='news-date', id=f'ContentPlaceHolder1_rptrNews_Label1_{i}').text.strip()
            title = a.find('a', id=f'ContentPlaceHolder1_rptrNews_hlnkNewsTitle_{i}').text.strip()
            full_text = a.find('span', class_='description', id=f'ContentPlaceHolder1_rptrNews_lblNewsDescription_{i}').text.strip()
            link = a.find('a')['href']
            data.append([date, title, full_text, link])
            cursor.execute('INSERT INTO sattlite (date, title, full_text, link) VALUES (?, ?, ?, ?)', (date, title, full_text, link))
        return data
    return None


def save_csv(data, filename):
    with open(filename, 'w', newline = '', encoding='utf-8') as file:
        wr = csv.writer(file)
        wr.writerow(['Date', 'Title', 'Full Text', 'Link'])
        wr.writerows(data)

def main():
    base_url = 'https://www.everythingrf.com/news?page='
    all_data = []
    page = requests.get(base_url)
    for page_num in range (1,11):
        url = base_url + str(page_num) + '&tags=satellite'
        page_data = parse_page(url)
        if page_data:
            all_data.extend(page_data)
    save_csv(all_data, 'satellite_news.csv')

db = sqlite3.connect('satellite.db')
cursor = db.cursor()

cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS sattlite (
        id INTEGER PRIMARY KEY, 
        date TEXT,
        title TEXT,
        full_text TEXT,
        link TEXT
        )
        '''
    )

main()


db.commit()
db.close()