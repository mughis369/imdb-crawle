from tabulate import tabulate

def get_improved_pops(**kwargs):
    movie_list = kwargs.get('movie_list', [])

    improved_movies = []
    for i, movie in enumerate(movie_list):
        if movie['popularity'][0:1] == '+':
            improved_movies.append([i + 1, movie['name'], movie['popularity']])

    print(tabulate(improved_movies, headers=["Pos", "Name", "Popularity"]))
    return improved_movies


def get_prev_positions(**kwargs):
    def _int(n):
        try:
            n = int(n)
        except:
            n = 0
        finally:
            return n

    movie_list = kwargs.get('movie_list', [])

    prev_ranks = []
    for i, movie in enumerate(movie_list):
        pop_trend = movie['popularity'][0:1]
        pop = _int(movie['popularity'][1:])
        pos = _int(movie['position'])
        ops = {
            '+': [abs(pop - pos), "UP"],
            '-': [pop + pos, "DOWN"]
        }
        prev_ranks.append([i + 1, movie['name'], ops[pop_trend][0], ops[pop_trend][1]])

    print(tabulate(prev_ranks, headers=["Current Pos", "Name", "Previous Pos", "Direction"]))
    return prev_ranks


def get_top_rated_genre(**kwargs):
    movie_list = kwargs.get('movie_list', [])

    gen_chart = {}
    for movie in movie_list:
        for gen in movie['genre']:
            if gen not in gen_chart:
                gen_chart[gen] = [int(movie['position'])]
            else:
                gen_chart[gen].append(int(movie['position']))

    gen_chart = [(gen, sum(count)//len(count)) for gen, count in gen_chart.items()]
    top_rated = sorted(gen_chart, key=lambda tup: tup[1])[0]
    
    print(f"{top_rated[0]} is most popular genre and has a avg position {top_rated[1]}")

    return top_rated

