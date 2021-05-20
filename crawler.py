#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import json

BASE_URL = "https://www.imdb.com"
MOST_POP_URL = "/chart/moviemeter?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=4da9d9a5-d299-43f2-9c53-f0efa18182cd&pf_rd_r=C45AMPS5DHYXD5MEAVEE&pf_rd_s=right-4&pf_rd_t=15506&pf_rd_i=moviemeter&ref_=chtmvm_ql_2"


def get_url_content(url):
    return requests.get(url).content


def extract_movie_list():
    res = get_url_content(BASE_URL + MOST_POP_URL)
    soup = BeautifulSoup(res, 'html.parser')
    
    urls = []
    count = 0
    for tag in soup.find_all('td', class_='titleColumn'):
        a = tag.find('a', href=True)
        year = return_ele(re.findall('[0-9]{4}', tag.get_text()), 0)
        urls.append(
            {
                'name': a.get_text(),
                'release_year': year,
                'link': BASE_URL + a['href']
            }
        )
        count += 1
    
    return urls


def return_ele(x, i):
    if len(x) > i: return x[i]


def extract_reviews(ele):
    revs = re.findall('[0-9]+', ele.get_text())
    return return_ele(revs, 0), return_ele(revs, 1)


def extract_popularity(ele):
    stats = re.findall('[0-9]+', ele.get_text())

    symbol = ele.find('span', class_='titleOverviewSprite popularityImageUp')
    if symbol is None:
        symbol = '-'
    else:
        symbol = '+'

    return return_ele(stats, 0), f"{symbol}{return_ele(stats, 1)}"


def extract_genre(ele):
    try:
        genre = ele.find_all('div', class_='see-more inline canwrap')[1].get_text()
    except:
        genre = ele.find_all('div', class_='see-more inline canwrap')[0].get_text()
    genre = genre.replace("Genres:", '').split('|')
    genre = [g.strip() for g in genre]

    return genre


def extract_movie_info(url, i):
    popularity = ''
    user_rev = ''
    critic_rev = ''
    position = ''

    res = get_url_content(url)
    soup = BeautifulSoup(res, 'html.parser')

    stats = soup.find_all('span', class_='subText')
    try:
        ratings = soup.find('span', {'itemprop':'ratingValue'}).get_text()
    except:
        ratings = ""
    
    if len(stats) == 1:
        position, popularity = extract_popularity(stats[0])
    elif len(stats) == 2:
        user_rev, critic_rev = extract_reviews(stats[0])
        position, popularity = extract_popularity(stats[1])
    elif len(stats) == 3:
        user_rev, critic_rev = extract_reviews(stats[1])
        position, popularity = extract_popularity(stats[2])

    genre = extract_genre(soup)

    return {
        'popularity'     : popularity,
        'position'       : position,
        'user_reviews'   : user_rev,
        'critic_reviews' : critic_rev,
        'ratings'        : ratings,
        'genre'          : genre
    }

def write(data):
    with open('movie_list.json', 'w') as f:
        json.dump(data, f, indent=4)


def start_scraper():
    movie_list = extract_movie_list()

    dicts = []
    for i, movie in enumerate(movie_list):
        print(" "*70, end='\r', flush=True)
        print(f"extracting info for {i + 1}: {movie['name']}...", end='\r', flush=True)
        
        info = extract_movie_info(movie['link'], i)
        info['name'] = movie['name']
        info['link'] = movie['link']
        info['release_year'] = movie['release_year']

        dicts.append(info)

    write(dicts)

start_scraper()