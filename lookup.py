import requests
import sys
import time
import operator
import difflib
from bs4 import BeautifulSoup


class quickSearch:

    def __init__(self, q) -> None:
        URL, query = self._start(q)
        self._main(URL, query)

    def _main(self, URL, query) -> None:
        raw_data = requests.get(URL)
        parsed_data = BeautifulSoup(raw_data.text, 'html.parser')

        parsed_links = []
        parse_words = ['/search', '/setprefs', 'google',
                       '/?sa', '/advanced_search', '/imgres']
        for link in parsed_data.find_all('a', href=True):
            if not any(word in link['href'] for word in parse_words):
                parsed_links.append(link['href'])

        parsed_links = [*set(parsed_links)]

        parsed_links = list(
            map(lambda x: x.split('/url?q=')[-1], parsed_links))

        parsed_links = list(map(lambda x: x.split('&sa')[0], parsed_links))

        sources = []
        for link in parsed_links:
            sources.append(link) if 'wiki' in link else False

        source_titles = list(map(lambda x: x.split('/')[-1], sources))

        def compareTo(x: str, y: str) -> float:
            return difflib.SequenceMatcher(a=x.lower(), b=y.lower()).ratio()

        ranks = list(map(lambda x: compareTo(x, query), source_titles))
        source_rank_dict = dict(zip(sources, ranks))
        source_ranks = sorted(source_rank_dict.items(),
                              key=lambda x: x[1], reverse=True)
        print()
        descs = []

        for index, source in enumerate(source_ranks):

            data = requests.get(source_ranks[index][0])
            data = BeautifulSoup(data.content, 'html.parser')
            paragraphs = data.find_all('p')
            texts = []

            for paragraph in paragraphs:
                texts.append(
                    "".join(map(str, paragraph.get_text().split('\n'))))

            text = "".join(map(str, texts))

            descs.append(text)

        def writeToScreen(text: str) -> None:
            for c in text:
                sys.stdout.write(c)
                sys.stdout.flush()
                time.sleep(0.0025)
        try:
            writeToScreen(f"{descs[0]} \n\n\n")
        except IndexError:
            print("401\nNo wiki availble for query")
        print()

    def _start(self, q_args) -> tuple:
        catch = 'https://www.google.com/search?q='
        query = ' '.join(map(str, q_args))

        standardized_query = query.replace(' ', '+')

        URL = catch + standardized_query
        return URL, query


if (__name__ == '__main__'):
    args = sys.argv[1:]
    if args:
        if '-q' in args:

            try:
                param = args.index('-q') + 1
                if args[param]:
                    quickSearch(q=args[param])
            except IndexError:
                print("param not found")
