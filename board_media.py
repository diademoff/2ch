import dvach
import imagecompare
from typing import List
import time
import os


class Hashtable:
    """Файл с информацией об уже скаченных картинках
    """
    path: str
    table: dict

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            open(path, 'w').close()
        self.load_file()

    def load_file(self):
        """Загрузить информацию из файла
        """
        self.table = dict()
        f = open(self.path)
        lines = f.readlines()
        for line in lines:
            try:
                hash = line.split('|')[0]
                path = line.split('|')[1]
                self.table[hash] = path
            finally:
                pass
        f.close()

    def add_image(self, path: str, hash: str):
        """Добавить изображение в словарь

        Args:
            path (str): путь к изображению
            hash (str): строковое представление изображения
        """
        try:
            self.table[hash] = path
        finally:
            pass

    def save_file(self):
        """Сохранить словарь в файл
        """
        f = open(self.path, 'w')
        f.write('')  # отчистить предыдущие
        for key in self.table.keys():
            hash = key
            path = self.table[key]
            line = f"{hash}|{path}\n"
            f.write(line)
        f.close()


# Скачать все файлы со всех тредов доски
BOARD = 'b'
FOLDER_NAME = 'media'  # название папки, куда будут скачиваться файлы
HASH_TABLE = os.path.normpath(f'{FOLDER_NAME}/hashtable')
KEY_WORDS = [  # список ключевых слов
    # "WEBM",
    # "webm",
    # "цуиь"
]


def IsOk(comment: str):
    """Подходит ли тред по ключевым словам

    Если хотя бы одно ключевое слово есть в тексте, тогда подходит.

    Args:
        comment (str): Текст в ОП-посте

    Returns:
        bool: Подходит ли по ключевым словам
    """
    if len(KEY_WORDS) != 0:
        for word in KEY_WORDS:
            if word in comment:
                return True  # подходит если есть одно из ключевых слов
    else:
        return True  # Подходит если ключевые слова не указаны.
    return False


def isImage(fileName: str):
    """Является ли файл .png или .jpg

    Args:
        fileName (str): имя файла
    """
    extention = fileName.split('.')[1]
    return extention == 'png' or extention == 'jpg'


def findInTable(hash: str):
    """Найти такую-же фотографию в базе

    Args:
        hash (str): строковое представление фото

    Returns:
        str: путь к такой же фотографии, если дубликата нет - пустая строка
    """
    if hash in hashtable.table.keys():
        return str(hashtable.table[hash]).strip()
    else:
        return ''


def download_thread_files(posts: List[dvach.Post], thread_num: str):
    """Скачать файлы постов треда

    Args:
        posts (List[dvach.Post]): список постов
    """
    for post in posts:
        for file in post.files:
            download_folder = os.path.normpath(FOLDER_NAME + f'/{thread_num}')
            download_path = os.path.normpath(f'{download_folder}/' + file.name)

            # Создаём папку с медиа треда
            if not os.path.exists(download_folder):
                os.mkdir(download_folder)
            if os.path.exists(download_path):
                # print(f'Файл {file.name} из треда {thread_num} существует')
                continue

            # try:
            file.save(download_path)

            if isImage(file.name):
                image_hash = imagecompare.CalcImageHash(download_path)
                same_photo = findInTable(image_hash)
                if same_photo != '':
                    os.remove(download_path)
                    os.symlink(os.path.abspath(same_photo), download_path, target_is_directory=False)
                    print(f'Дубликат {download_path} обнаружен в {same_photo}. Ссылка создана')
                    continue
                hashtable.add_image(download_path, imagecompare.CalcImageHash(download_path))

            print(f'Скачен файл из треда {thread_num}: {file.name}')
            time.sleep(0.1)
            # except:
            #     # Если не получилось скачать файл
            #     print('.', end='')
            #     time.sleep(3)


def search_threads(board: dvach.Board):
    """Скачать файлы из тредов, которые подходят по ключевым словам

    Args:
        board (dvach.Board): доска, на которой искать треды
    """
    for thread_num in board.threads.keys():
        # Тред с которого скачивать файлы
        thread = board.threads[thread_num]

        if not IsOk(thread.comment):
            continue  # Если не подходит - пропускаем

        # Скачиваем посты треда
        try:
            thread.update_posts()
        except:
            # Если не получислось скачать список постов
            time.sleep(3)
            continue

        # Скачиваем файлы в папку media/{thread_num}
        download_thread_files(thread.posts, thread.num)


if __name__ == '__main__':
    # Создаём папку с медиа
    if not os.path.exists(FOLDER_NAME):
        os.mkdir(FOLDER_NAME)

    global hashtable
    hashtable = Hashtable(HASH_TABLE)

    # Скачиваем доску с тредами
    board = dvach.Board(BOARD)
    while True:
        try:
            board.update_threads()
        except:
            # Если не получилось скачать список тредов
            time.sleep(3)
            continue

        # Обойти все треды и выбрать те, с которых скачивать файлы
        # Затем скачать файлы
        search_threads(board)
        print('Сохранение таблицы изображений')
        hashtable.save_file()
