#!/usr/bin/env python3
import analyzer
import crawler
import utils
import sys


__verbosity = False
startup_msg = '''This program performs user actions interactivly, 
the operations user can perform are listed as:'''
menu = '''
Enter 1 to fetch latest movies from popular movies list,
Enter 2 to veiw movie list that have improved in popularity,
Enter 3 to view previous week's positions,
Enter 4 to see top rated genre,
Enter n/N to exit'''
help='''
Further following switches can be used to do some extra stuff

 -h : this switch shows the help page.  

Example:
    python main.py -h    # prints the help page
    python main.py       # starts the program for interactive session

'''

def print_help():
    print(f"{startup_msg}{menu}{help}")


def main():
    movie_list = utils.read()

    features = {
        '1': crawler.start_scraper,
        '2': analyzer.get_improved_pops,
        '3': analyzer.get_prev_positions,
        '4': analyzer.get_top_rated_genre
    }
    
    def run():
        while True:
            choice = input(f"{menu}: ")
            utils.validate_choice(choice)
            
            func = features.get(choice, None)
            if func:
                result = func(movie_list=movie_list, verbose=__verbosity)
            else:
                print(f"Invalid operation: {choice}")
                result = None
            
            choice = input('Continue? (y/n): ')
            utils.validate_choice(choice)

    args = sys.argv[1:]
    if args:
        if args[0] == '-h':
            print_help()
        else:
            print("Invalid Opetion, see the help below to run the program:")
            print_help()
    else:
        run()

main()