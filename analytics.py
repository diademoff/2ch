import json
import time
import requests
import sys
import os
from bs4 import BeautifulSoup


class Post:
    pass


class Thread:
    """Тред борды."""
    comment: str
    lasthit: int
    num: str
    posts_count: int
    score: float
    subject: str
    timestamp: int
    views: int

    board_name: str
    posts = []
    score_history = []

    def __init__(self, board_name: str, json_thread_data):
        """Инициализация треда."""
        if json_thread_data != '':
            self.comment = json_thread_data['comment']
            self.lasthit = int(json_thread_data['lasthit'])
            self.num = json_thread_data['num']
            self.posts_count = int(json_thread_data['posts_count'])
            self.score = float(json_thread_data['score'])
            self.subject = json_thread_data['subject']
            self.timestamp = int(json_thread_data['timestamp'])
            self.views = int(json_thread_data['views'])
            # clean comments
            self.comment = BeautifulSoup(self.comment, 'lxml').text.strip()

            self.score_history = [self.score]
        self.board_name = board_name

    @property
    def get_link(self) -> str:
        """Ссылка на тред"""
        return f'https://2ch.hk/{self.board_name}/res/{self.num}.html'


class BoardRefreshInfo:
    """Информация об изменениях на борде."""

    deadThreads = []
    newThreads = []

    def __init__(self, deadThreads, newThreads):
        """Инициализация"""
        self.deadThreads = deadThreads
        self.newThreads = newThreads


class Board:
    """Борда."""

    name: str
    threads: dict

    def __init__(self, name: str):
        """Инициализировать борду. Пример имени: `b`."""
        self.name = name
        self.threads = dict()

    def reload_threads(self):
        """Скачать json и спарсить треды."""
        try:
            json_downloaded = requests.get(self.json_link, stream=True).text
            json_data = json.loads(json_downloaded)
            threads_json = json_data['threads']
        except:
            return None

        downloaded_threads = dict()
        for thread_json in threads_json:
            thread = Thread(self.name, thread_json)
            downloaded_threads[thread.num] = thread

        dead = self.get_dead_threads(downloaded_threads)
        new = self.get_new_threads(downloaded_threads)

        # Remove dead
        for d in dead.keys():
            self.threads.pop(dead[d].num)

        # Add new
        for n in new.keys():
            self.threads[new[n].num] = new[n]

        # Save score histry
        for t in downloaded_threads.keys():
            dw_thread = downloaded_threads[t]
            if dw_thread.num not in self.threads.keys():
                self.threads[dw_thread.num] = dw_thread
                continue
            if self.threads[dw_thread.num].score_history[-1] != dw_thread.score:
                self.threads[dw_thread.num].score_history.append(dw_thread.score)

        return BoardRefreshInfo(dead, new)

    def sort_threads_by_score(self):
        """Отсортировать треды по очкам."""
        for i in range(len(self.threads.keys())):
            for j in range(len(self.threads.keys())):
                key_i = list(self.threads.keys())[i]
                key_j = list(self.threads.keys())[j]
                if self.threads[key_i].score > self.threads[key_j].score:
                    self.threads[key_i], self.threads[key_j] = self.threads[key_j], self.threads[key_i]

    def get_dead_threads(self, comparewith):
        """`comparewith` это список тредов, который был в прошлой раз."""
        dead = dict()
        for old in self.threads.keys():
            if not (old in comparewith.keys()):
                dead[str(old)] = self.threads[old]
        return dead

    def get_new_threads(self, comparewith):
        """`comparewith` это список тредов, который был в прошлой раз."""
        new_threads = dict()
        for new in comparewith.keys():
            if not (new in self.threads.keys()):
                new_threads[str(new)] = comparewith[new]
        return new_threads

    @property
    def thread_exists(self, num: str) -> bool:
        """Существует ли тред."""
        for thread in self.threads:
            if thread.num == num:
                return True
        return False

    @property
    def json_link(self):
        """Ссылка на список тредов json."""
        return f'http://2ch.hk/{self.name}/threads.json'


def show_popular(num: int, board='b'):
    b = Board(board)
    while True:
        res = b.reload_threads()
        b.sort_threads_by_score()
        os.system('clear')

        print('Most popular: ')

        for i in range(num):
            if not (i < len(b.threads)):
                break
            t = b.threads[list(b.threads.keys())[i]]

            str_status = '⬦'
            if len(t.score_history) > 2:
                if t.score_history[-2] < t.score_history[-1]:
                    str_status = '↑'
                elif t.score_history[-2] == t.score_history[-1]:
                    str_status = '⬦'
                else:
                    str_status = '↓'

            text_limit = 155
            comment_formatted = ('{0:' + str(text_limit) + '}').format(t.comment[:text_limit:])
            score_formated = '{0:3}'.format(round(t.score))
            posts_count_formatted = '{0:3}'.format(t.posts_count)
            print(f"{str_status} /{board} scr:{score_formated}:{posts_count_formatted} | {comment_formatted} | {t.get_link}")

        if res is None:
            print('Refresh error')

        time.sleep(15)

def show_tracker(boards_list='b news sex v hw gg dev soc rf ma psy fet'):
    boards = []
    print('Scanning...')
    for b in boards_list.split(' '):
        boards.append(Board(b))
        while True:
            r = boards[-1].reload_threads()
            if not (r is None):
                break
            time.sleep(5)
    print('Done')
    
    while True:
        for b in boards:
            info = b.reload_threads()

            if info is None:
                print('.',end='')
                continue

            board_name = '{0:5}'.format(b.name)
            text_limit = 155

            for n in info.newThreads:
                thread = info.newThreads[n]
                comment_formatted = ('{0:' + str(text_limit) + '}').format(thread.comment[:text_limit:])
                print(f"Новый на /{board_name} | {comment_formatted} | {thread.get_link}")
                os.system(f'notify-send -t 23000 \"/{board_name} {thread.comment}\"')
                time.sleep(2)

        time.sleep(7)

if __name__ == "__main__":

    for arg in sys.argv:
        if 'popular' in arg:
            show_popular(int(arg.split('=')[1]))
        elif arg == 'tracker':
            show_tracker()

    print('Запустите с использование параметров:')
    print('popular=[num] - отображать самые популярные треды')
    print('tracker - мониторить новые треды')