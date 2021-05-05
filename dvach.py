import json
from typing import List
import requests
from bs4 import BeautifulSoup


class Post_file:
    displayname: str
    name: str
    path: str
    width: int
    height: int
    size: int

    def __init__(self, json_data):
        self.displayname = json_data['displayname']
        self.name = json_data['name']
        self.path = json_data['path']
        self.width = json_data['width']
        self.height = json_data['height']
        self.size = json_data['size']

    def save(self, path: str):
        r = requests.get(self.download_link)
        with open(path, 'wb') as output:
            output.write(r.content)

    def IsOk(self, EXTENSIONS: List[str], MAX_FILE_SIZE: int, MIN_FILE_SIZE: int):
        """Подходит ли файл по заданным расширениям, максимальному и минимальному размеру

        Args:
            EXTENSIONS (List[str]): Список разрешенных расширений
            MAX_FILE_SIZE (int): Максимальный размер файла
            MIN_FILE_SIZE (int): Минимальный размер файла

        Returns:
            bool: Подходит ли
        """
        if self.name.split('.')[1].lower() not in EXTENSIONS:
            return False

        if MAX_FILE_SIZE != 0 and self.size > MAX_FILE_SIZE:
            return False

        if MIN_FILE_SIZE != 0 and self.size < MIN_FILE_SIZE:
            return False

        return True

    @property
    def download_link(self):
        return f'https://2ch.hk{self.path}'


class Post:
    comment: str
    num: str
    files: List[Post_file]

    def __init__(self, json_post_data):
        self.comment = BeautifulSoup(json_post_data['comment'], 'lxml').text.strip()
        self.num = json_post_data['num']
        self.files = []
        for json_file_data in json_post_data['files']:
            self.files.append(Post_file(json_file_data))


class Thread:
    """Тред доски."""
    comment: str
    lasthit: int
    num: str
    posts_count: int
    score: float
    subject: str
    timestamp: int
    views: int
    unique_posters: int  # определяется по оп посту

    board_name: str  # тред должен знать на какой он доске
    posts = []
    score_history = []

    def __init__(self, board_name: str, json_thread_data=''):
        """
        Инициализация треда.

        json_thread_data - json от доски (там нет списка постов)
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

    def update_posts(self):
        """Скачать посты и обновить их список
        """
        json_posts = self.json_download()
        self.get_posts(json_posts)

    def get_posts(self, json_posts):
        """Перезаписать список постов в треде из json"""
        posts_json = json.loads(json_posts)
        self.unique_posters = int(posts_json[0]['unique_posters'])
        self.posts = []
        for post in posts_json:
            self.posts.append(Post(post))

    def get_hierarchy(self, html_thread):
        """
        Получить иерархию тредов (без учета ОП-поста).

        Ключ является номером поста, значение - это список ответов на пост
        """
        ref_map = {}

        soup = BeautifulSoup(html_thread, "lxml")
        posts = soup.find_all('div', class_="thread__post")

        for post in posts:
            post_num = str(post.get('id'))
            post_num = post_num.split('-')[1]

            refmap = post.find_all('div', class_='post__refmap')[0]
            refs = refmap.find_all('a', class_='post-reply-link')

            ref_map[post_num] = []
            for ref in refs:
                ref_map[post_num].append(str(ref.get('data-num')))

        return ref_map

    def IsOk(self, KEY_WORDS: List[str]):
        """Подходит ли тред по ключевым словам

        Если хотя бы одно ключевое слово есть в тексте, тогда подходит.

        Args:
            KEY_WORDS (List[str]): Ключевые слова

        Returns:
            bool: Подходит ли по ключевым словам
        """
        if len(KEY_WORDS) != 0:
            for word in KEY_WORDS:
                if word in self.comment.lower():
                    return True  # подходит если есть одно из ключевых слов
        else:
            return True  # Подходит если ключевые слова не указаны.
        return False

    def json_download(self):
        """Скачать json постов

        Returns:
            str: json постов
        """
        return download_json(self.json_posts_link)

    @property
    def json_posts_link(self) -> str:
        return f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={self.board_name}&thread={self.num}&post=1"

    @property
    def get_link(self) -> str:
        """Ссылка на тред"""
        return f'https://2ch.hk/{self.board_name}/res/{self.num}.html'


class BoardRefreshInfo:
    """Информация об изменениях на доске."""

    deadThreads = []
    newThreads = []

    def __init__(self, deadThreads, newThreads):
        """Инициализация"""
        self.deadThreads = deadThreads
        self.newThreads = newThreads


class Board:
    """Доска."""

    name: str
    threads: dict

    def __init__(self, name: str, threads=dict()):
        """Инициализировать доску. Пример имени: `b`."""
        self.name = name
        self.threads = threads

    @staticmethod
    def from_json(json_text: str):
        """Спарсить json и вернуть доску

        Args:
            json_text (str): json с списом тредов и именем доски

        Returns:
            Board: Возвращает доску сформированную из json
        """
        json_data = json.loads(json_text)
        threads_json = json_data['threads']
        name_json = json_data['board']

        downloaded_threads = dict()
        for thread_json in threads_json:
            thread = Thread(name_json, thread_json)
            downloaded_threads[thread.num] = thread

        return Board(name_json, downloaded_threads)

    def sort_threads_by_score(self):
        """Сортировка тредов по очкам
        """
        for i in range(len(self.threads.keys())):
            for j in range(len(self.threads.keys())):
                key_i = list(self.threads.keys())[i]
                key_j = list(self.threads.keys())[j]
                if self.threads[key_i].score > self.threads[key_j].score:
                    self.threads[key_i], self.threads[key_j] = self.threads[key_j], self.threads[key_i]

    def update_threads(self):
        self.threads = Board.from_json(Board.json_download(self.name)).threads

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
    """Скачать json

    Args:
        link (str): ссылка на скачивание

    Returns:
        str: возвращает json
    """
    return requests.get(link, stream=True).text
