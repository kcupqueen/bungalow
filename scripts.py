from typing import List, Tuple

from mdict_query import IndexBuilder
from bs4 import BeautifulSoup


class Word(object):
    def __init__(self, word: str, pattern: str):
        self.sense = []
        self.word = word
        self.pattern = pattern

    def __str__(self):
        fist_line = f'word: {self.word} pattern: {self.pattern}\n'
        second_line = ''
        for sense in self.sense:
            second_line += f'SENSE: {sense[0]}\n'
            for example in sense[1]:
                second_line += f'EXAMPLE: {example}\n'

        return f'{fist_line}{second_line}'

    def to_html(self):
        html = f'<h1>{self.word}</h1>'
        for sense in self.sense:
            html += f'<p><b>{sense[0]}</b></p>'
            for example in sense[1]:
                html += f'<p>{example}</p>'

        return html

    def __repr__(self):
        return self.__str__()

    def add_sense(self, sense: str):
        self.sense.append([sense, []])

    def add_example(self, example: str):
        self.sense[-1][1].append(example)


def link_to_word(link: str):
    if link.startswith('@@@LINK='):
        # print('found LINK=')
        return link[8:]
    return None


def parse_pattern(string: str, raw_word: str):
    soup = BeautifulSoup(string, 'html.parser')
    if soup.find('span', {'class': 'sense newline'}):
        sense_class_name = 'sense newline'
    elif soup.find('span', {'class': 'sense'}):
        sense_class_name = 'sense'
    else:
        raise Exception('No sense class found')

    _word = Word(word=raw_word, pattern=sense_class_name)
    sense_new_line_list = soup.findAll('span', {'class': sense_class_name})
    previous_phrase = None
    for sense_new_line in sense_new_line_list:
        if sense_new_line.findParent('span', {'class': 'phrvbentry'}):

            parent_phrase = sense_new_line.findParent('span', {'class': 'phrvbentry'})
            phrase = parent_phrase.find('span', {'class': 'phrvbhwd'}).text

            if previous_phrase != phrase:
                print('phrase is: ', phrase)
            previous_phrase = phrase

        # print(sense_new_line.find_next('span', {'class': 'sensenum'}).text)
        sense_number = sense_new_line.find_next('span', {'class': 'sensenum'})
        if sense_number:
            # print(sense_number.text)
            pass
        sense_def = sense_new_line.find_next('span', {'class': 'def'})
        en = sense_def.find_next('en')
        trans = sense_def.find_next('tran')
        _word.add_sense(en.text.strip() + " " + trans.text.strip())

        sense_example = sense_new_line.findAll('span', {'class': 'example'})
        # print(f'has {len(sense_example)} examples')
        for example in sense_example:
            if example.find('exaen'):
                print(example.find('exaen').text.strip())
                _word.add_example(example.find('exaen').text.strip())
    return _word


def print_formatted(string: str):
    soup = BeautifulSoup(string, 'html.parser')
    print(soup.prettify())


def read_words(file_path: str):
    # txt format
    with open(file_path, encoding='utf-8') as f:
        words = f.readlines()
    for word in words:
        word = word.strip()
        # example: 9@budge@v.  移动； 妥协 n.  羔皮 adj.  浮夸的； 庄严的
        word = word.split('@')[1]
        yield word


if __name__ == '__main__':
    words = read_words('./words/words.txt')
    builder = IndexBuilder('E:\Game\En101\midict\Android\longman.mdx')
    for word in words:
        result_text = builder.mdx_lookup(word)
        text = result_text[0]
        if link_to_word(text):
            word = link_to_word(text).strip()
            # print('link to word: ',word)
            result_text = builder.mdx_lookup(word)
            # print(result_text)
            text = result_text[0]

        # print_formatted(text)
        content = parse_pattern(text, word)
        print_formatted(content.to_html())
