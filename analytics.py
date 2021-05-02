import json
import time
import requests
import sys
import os
from bs4 import BeautifulSoup


class Post_file:
    displayname: str
    name: str
    path: str
    width: int
    height: int

    def __init__(self, json_data):
        self.displayname = json_data['displayname']
        self.name = json_data['name']
        self.path = json_data['path']
        self.width = json_data['width']
        self.height = json_data['height']

    def save(self, path: str):
        r = requests.get(self.download_link)
        with open(path, 'wb') as output:
            output.write(r.content)

    @property
    def download_link(self):
        return f'https://2ch.hk{self.path}'


class Post:
    comment: str
    num: str
    files: []

    def __init__(self, json_post_data):
        self.comment = json_post_data['comment']
        self.num = json_post_data['num']
        self.files = []
        for json_file_data in json_post_data['files']:
            self.files.append(Post_file(json_file_data))


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

    board_name: str  # тред должен знать на какой он борде
    posts = []
    score_history = []

    def __init__(self, board_name: str, json_thread_data=''):
        """
        Инициализация треда.

        json_thread_data - json от борды (там нет списка постов)
        """
        if json_thread_data != '':
            self.comment = json_thread_data['comment']
            self.lasthit = int(json_thread_data['lasthit'])
            self.num = json_thread_data['num']
            self.posts_count = int(json_thread_data['posts_count'])
            self.score = float(json_thread_data['score'])
            self.subject = json_thread_data['subject']
            self.timestamp = int(json_thread_data['timestamp'])
            self.views = int(json_thread_data['views'])
            # отчистить от html
            self.comment = BeautifulSoup(self.comment, 'lxml').text.strip()

            self.score_history = [self.score]
        self.board_name = board_name

    def get_posts(self, json_posts):
        """Перезаписыват посты в треде из json"""
        posts_json = json.loads(json_posts)
        self.posts = []
        for post in posts_json:
            self.posts.append(Post(post))

    def json_download(self):
        return download_json(self.json_posts_link)

    @property
    def json_posts_link(self) -> str:
        return f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={self.board_name}&thread={self.num}&post=1"

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

    def __init__(self, name: str, threads=dict()):
        """Инициализировать борду. Пример имени: `b`."""
        self.name = name
        self.threads = threads

    @staticmethod
    def from_json(json_text: str):
        """Спарсить json и вернуть борду"""
        json_data = json.loads(json_text)
        threads_json = json_data['threads']
        name_json = json_data['board']

        downloaded_threads = dict()
        for thread_json in threads_json:
            thread = Thread(name_json, thread_json)
            downloaded_threads[thread.num] = thread

        return Board(name_json, downloaded_threads)

    def sort_threads_by_score(self):
        """Отсортировать треды по очкам."""
        for i in range(len(self.threads.keys())):
            for j in range(len(self.threads.keys())):
                key_i = list(self.threads.keys())[i]
                key_j = list(self.threads.keys())[j]
                if self.threads[key_i].score > self.threads[key_j].score:
                    self.threads[key_i], self.threads[key_j] = self.threads[key_j], self.threads[key_i]

    def get_dead_threads(self, comparewith):
        """`comparewith` это новый список тредов"""
        dead = dict()
        for t in self.threads.keys():
            if t not in comparewith.keys():
                dead[str(t)] = self.threads[t]
        return dead

    def get_new_threads(self, comparewith):
        """`comparewith` это новый список тредов"""
        new_threads = dict()
        for new in comparewith.keys():
            if not (new in self.threads.keys()):
                new_threads[str(new)] = comparewith[new]
        return new_threads

    @staticmethod
    def json_download(board_name: str) -> str:
        """Скачать json."""
        download_link = Board(board_name).json_link
        json_downloaded = requests.get(download_link, stream=True).text
        return json_downloaded

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


def download_json(link: str) -> str:
    return requests.get(link, stream=True).text


if __name__ == "__main__":
    pass
