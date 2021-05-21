#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import utils

BASE_URL = "https://www.imdb.com"
MOST_POP_URL = "/chart/moviemeter?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=4da9d9a5-d299-43f2-9c53-f0efa18182cd&pf_rd_r=C45AMPS5DHYXD5MEAVEE&pf_rd_s=right-4&pf_rd_t=15506&pf_rd_i=moviemeter&ref_=chtmvm_ql_2"


def get_url_content(url):
    return requests.get(url).content


def extract_movie_list():
    res = get_url_content(BASE_URL + MOST_POP_URL)
    soup = BeautifulSoup(res, 'html.parser')
    
    m_list = []
    count = 0
    for tag in soup.find_all('td', class_='titleColumn'):
        a = tag.find('a', href=True)
        year = utils.return_ele(re.findall('[0-9]{4}', tag.get_text()), 0)
        m_list.append(
            {
                'name': a.get_text(),
                'release_year': year,
                'link': BASE_URL + a['href']
            }
        )
        count += 1
    
    return m_list


def extract_reviews(ele):
    revs = re.findall('[0-9]+', ele.get_text())
    return utils.return_ele(revs, 0), utils.return_ele(revs, 1)


def extract_popularity(ele):
    stats = re.findall('[0-9]+', ele.get_text())

    symbol = ele.find('span', class_='titleOverviewSprite popularityImageUp')
    if symbol is None:
        symbol = '-'
    else:
        symbol = '+'

    return utils.return_ele(stats, 0), f"{symbol}{utils.return_ele(stats, 1)}"


def extract_genre(ele):
    try:
        genre = ele.find_all('div', class_='see-more inline canwrap')[1].get_text()
    except:
        genre = ele.find_all('div', class_='see-more inline canwrap')[0].get_text()
    finally:
        genre = genre.replace("Genres:", '').split('|')
        genre = [g.strip() for g in genre]

        return genre


def extract_ratings(ele):
    try:
        ratings = ele.find('span', {'itemprop':'ratingValue'}).get_text()
    except:
        ratings = ""
    finally:
        return ratings


def extract_stats(ele):
    popularity = ''
    user_rev = ''
    critic_rev = ''
    position = ''

    stats = ele.find_all('span', class_='subText')

    if len(stats) == 1:
        position, popularity = extract_popularity(stats[0])
    elif len(stats) == 2:
        user_rev, critic_rev = extract_reviews(stats[0])
        position, popularity = extract_popularity(stats[1])
    elif len(stats) == 3:
        user_rev, critic_rev = extract_reviews(stats[1])
        position, popularity = extract_popularity(stats[2])

    return position, popularity, user_rev, critic_rev


def extract_movie_info(url):
    popularity = ''
    position = ''
    user_rev = ''
    critic_rev = ''
    ratings = ''
    genre = []
    
    try:
        res = get_url_content(url)
        soup = BeautifulSoup(res, 'html.parser')

        ratings = extract_ratings(soup)
        position, popularity, user_rev, critic_rev = extract_stats(soup)
        genre = extract_genre(soup)

    except Exception as e:
        pass
        # print(f"Exception: {e.__str__()}")
    finally:
        return {
            'popularity'     : popularity,
            'position'       : position,
            'user_reviews'   : user_rev,
            'critic_reviews' : critic_rev,
            'ratings'        : ratings,
            'genre'          : genre
        }


def scrape(movie):
    print(" "*70, end='\r', flush=True)
    print(f"extracting info for ({movie['name']})...", end='\r', flush=True)
    
    info = extract_movie_info(movie['link'])
    movie.update(info)

    return movie


def start_scraper(**kwargs):
    from concurrent.futures import ThreadPoolExecutor
    from datetime import datetime

    max_workers = kwargs.get('max_workers', 10)
    movie_list = extract_movie_list()

    start_time = datetime.now()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        result = executor.map(scrape, movie_list, timeout=8)
    movie_list = list(result)
    end_time = datetime.now()

    msg = f'''It took me {(end_time - start_time).total_seconds()}seconds to complete the scrape:
    Movies Scraped: {len(movie_list)}
    No. of Workers: {max_workers}'''
    utils.write(movie_list, msg)
