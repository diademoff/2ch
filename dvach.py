import json
from typing import List
import requests
from bs4 import BeautifulSoup
import os
from requests.models import Response

headers = {
    "Accept": "image/webp,*/*",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Cookie": "usercode_auth=3c86e2be7602c264ffddd9723be0688b; wakabastyle=Futaba;"
}


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
        """Сохранить файл

        Args:
            path (str): Путь к файлу, в которой сохранить файл
        """
        if os.path.isdir(path):
            raise Exception("Вы указали папку, но требуется файл")
        r = download_link(self.download_link)
        with open(path, 'wb') as output:
            output.write(r.content)

    @property
    def IsImage(self) -> bool:
        """Является ли файл .png или .jpg

        Args:
            fileName (str): имя файла
        """
        ext = self.name.split('.')[1]
        return ext == 'png' or ext == 'jpg'

    @property
    def IsVideo(self) -> bool:
        """Является ли файл видео
        """
        # Так как файл либо фото, либо видео
        return not self.IsImage

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
    comment_html: str  # не очищенное от html
    date: str
    email: str
    op: int
    num: str
    files: List[Post_file]

    def __init__(self, json_post_data):
        self.comment = json_post_data['comment']
        # отчистить если есть открывающий тег
        if '<' in self.comment:
            self.comment = BeautifulSoup(json_post_data['comment'], 'lxml').text.strip()
        self.comment_html = json_post_data['comment']
        self.num = str(json_post_data['num'])
        self.date = json_post_data['date']
        self.email = json_post_data['email']
        self.op = json_post_data['op']
        self.files = []
        if json_post_data.get('files'):
            for json_file_data in json_post_data['files']:
                self.files.append(Post_file(json_file_data))


class Thread:
    """Тред доски."""
    comment: str
    comment_html: str  # не очищенное от html
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
            self.comment_html = json_thread_data['comment']
            self.lasthit = int(json_thread_data['lasthit'])
            self.num = json_thread_data['num']
            self.posts_count = int(json_thread_data['posts_count'])
            self.score = float(json_thread_data['score'])
            self.subject = json_thread_data['subject']
            self.timestamp = int(json_thread_data['timestamp'])
            self.views = int(json_thread_data['views'])
            # отчистить от html, если есть открывающий тег
            if '<' in self.comment:
                self.comment = BeautifulSoup(self.comment, 'lxml').text.strip()

            self.score_history = [self.score]
        self.board_name = board_name

    @property
    def get_op_post(self):
        if len(self.posts) == 0:
            raise Exception("Посты не скачаны")
        return self.posts[0]

    def get_op_img_path(self) -> str:
        """Получить путь к скаченному изображению из ОП-поста. Видео игнорируются

        Returns:
            str: путь к изображению или пустая строка
        """
        if len(self.posts) == 0:
            raise Exception("Посты не скачаны")
        files = self.posts[0].files
        for file in files:
            if file.IsImage:
                path = os.path.normpath(f'{file.name}')
                return path
        return ""

    def save(self, folder_path: str) -> str:
        """Сохранить тред в папку (html файл)

        Args:
            folder_path (str): папка, в которую сохранять

        Returns:
            str: путь, куда сохранен файл
        """
        if len(self.posts) == 0:
            raise Exception("Посты не скачаны")
        if os.path.isfile(folder_path):
            raise Exception("Вы указали файл, но требуется директория")

        img_path = self.get_op_img_path()
        html = HtmlGenerator.get_thread_htmlpage(self, img_path)
        save_path = os.path.normpath(f'{folder_path}/thread_{self.num}.html')
        open(save_path, 'w', encoding='utf-8').write(html)
        return save_path

    def update_posts(self):
        """Скачать посты и обновить их список"""
        json_posts = self.json_download()
        self.get_posts(json_posts)

    def get_posts(self, json_posts):
        """Перезаписать список постов в треде из json"""
        posts_json = json.loads(json_posts)
        self.unique_posters = int(posts_json['unique_posters'])
        self.posts = []
        for post in posts_json['threads'][0]['posts']:
            self.posts.append(Post(post))

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

    def json_download(self) -> str:
        """Скачать json постов

        Returns:
            str: json постов
        """
        return download_link(self.json_posts_link).text

    @property
    def json_posts_link(self) -> str:
        # return f"https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={self.board_name}&thread={self.num}&post=1"
        return f"https://2ch.hk/{self.board_name}/res/{self.num}.json"

    @property
    def get_link(self) -> str:
        """Ссылка на тред"""
        return f'https://2ch.hk/{self.board_name}/res/{self.num}.html'


class BoardRefreshInfo:
    """Информация об изменениях на доске."""

    deadThreads = List[Thread]
    newThreads = List[Thread]

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

    def sort_threads_by_posts(self):
        """ Сортировка тредов по количеству постов"""
        for i in range(len(self.threads.keys())):
            for j in range(i, len(self.threads.keys())):
                key_i = list(self.threads.keys())[i]
                key_j = list(self.threads.keys())[j]
                if self.threads[key_i].posts_count < self.threads[key_j].posts_count:
                    self.threads[key_i], self.threads[key_j] = self.threads[key_j], self.threads[key_i]

    def update_threads(self):
        """ Скачать треды"""
        self.threads = Board.from_json(Board.json_download(self.name)).threads

    def get_dead_threads(self, comparewith):
        """`comparewith` это новый скачанный список тредов с которым сравнивать текущие треды"""
        dead = dict()
        for t in self.threads.keys():
            if t not in comparewith.keys():
                dead[str(t)] = self.threads[t]
        return dead

    def get_new_threads(self, comparewith):
        """`comparewith` это новый скачанный список тредов с которым сравнивать текущие треды"""
        new_threads = dict()
        for new in comparewith.keys():
            if not (new in self.threads.keys()):
                new_threads[str(new)] = comparewith[new]
        return new_threads

    @staticmethod
    def json_download(board_name: str) -> str:
        """Скачать json"""
        link = Board(board_name).json_link
        json_downloaded = download_link(link).text
        return json_downloaded

    def thread_exists(self, num: str) -> bool:
        """Существует ли тред"""
        for thread in self.threads:
            if thread.num == num:
                return True
        return False

    @property
    def json_link(self) -> str:
        """Ссылка на список тредов json"""
        return f'https://2ch.hk/{self.name}/threads.json'


class HtmlGenerator:
    """Создаёт html-страницу"""

    @staticmethod
    def _read_block(name: str) -> str:
        return open(os.path.normpath(f'page_gen/blocks/{name}'), encoding='utf-8').read()

    @staticmethod
    def _replace_str_in_html(html: str, key: str, value: str):
        """Заменить значения в фигурных скобах на нужные

        Args:
            html (str): сам код
            key (str): что заменить, например "{num}"
            value (str): на что заменить

        Returns:
            str: возвращает исправленный html
        """
        return html.replace(key, value)

    @staticmethod
    def get_htmlhead(thread: Thread) -> str:
        return f"""
        <head>
            <meta charset="UTF-8">
            <meta http-equiv="X-UA-Compatible" content="IE=edge">
            <style>
                {open(os.path.normpath(f'page_gen/style.css'), encoding='utf-8').read()}
            </style>
            <title>{thread.get_op_post.comment}</title>
        </head>
        """

    @staticmethod
    def get_htmldashboard() -> str:
        return HtmlGenerator._read_block('dashboard.html')

    @staticmethod
    def get_js_script() -> str:
        return HtmlGenerator._read_block('script.js')

    @staticmethod
    def get_post_images(post: Post) -> str:
        # <img src="{img_src}" alt="" style="max-height:70px">
        images = []  # Изображения поста (видео игнорируются)
        for file in post.files:
            if file.IsImage:
                images.append(file)

        result_html = ""
        for i in images:
            img_path = i.name
            image_html = f"<img src=\"{img_path}\" alt=\"\" style=\"max-height:70px\">\n"
            result_html += f"<a href=\"{img_path}\" target=\"_blank\">{image_html}</a>\n"
        return result_html

    @staticmethod
    def get_post_htmlpage(post: Post, order: int) -> str:
        """ html для одного поста"""
        htmlcode = HtmlGenerator._read_block('post.html')
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{date}', post.date)
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{num}', str(post.num))
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{order}', str(order))
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{msg}', post.comment_html)
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{answers}', "")
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{images}', HtmlGenerator.get_post_images(post))
        return htmlcode

    @staticmethod
    def get_posts_htmlpage(thread: Thread) -> str:
        posts: List[Post] = thread.posts[1:]  # Без оп-поста
        htmlcode = ""
        for i in range(0, len(posts)):
            htmlcode += HtmlGenerator.get_post_htmlpage(posts[i], i + 2)
        return htmlcode

    @staticmethod
    def get_op_post_htmlpage(thread: Thread, img_src: str) -> str:
        htmlcode = HtmlGenerator._read_block('op_post.html')
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{date}', thread.get_op_post.date)
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{num}', str(thread.num))
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{img_src}', img_src)
        htmlcode = HtmlGenerator._replace_str_in_html(htmlcode, '{msg}', thread.comment_html)
        return htmlcode

    @staticmethod
    def get_thread_htmlpage(thread: Thread, img_src: str) -> str:
        """ Создать html страницу для треда"""
        code = f"""
        <!DOCTYPE html>
        <html lang="ru">
        {HtmlGenerator.get_htmlhead(thread)}
        <body>
            {HtmlGenerator.get_htmldashboard()}
            <div class="container">
                {HtmlGenerator.get_op_post_htmlpage(thread, img_src)}
                {HtmlGenerator.get_posts_htmlpage(thread)}
            </div>
            <script>
                {HtmlGenerator.get_js_script()}
            </script>
        </body>
        </html>
        """
        return code


def download_link(link: str, retries=3) -> Response:
    """Скачать json

    Args:
        link (str): ссылка на скачивание
    """
    for _ in range(retries):
        try:
            return requests.get(link, timeout=15, stream=True)
        except requests.exceptions.SSLError as e:
            time.sleep(1)
    raise

