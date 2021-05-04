import dvach
from typing import List
import time
import os

# Скачать все файлы со всех тредов доски
BOARD = 'b'
FOLDER_NAME = 'media'  # название папки, куда будут скачиваться файлы
KEY_WORDS = [  # список ключевых слов
    "WEBM",
    "webm",
    "цуиь"
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
            try:
                file.save(download_path)
                print(f'Скачен файл из треда {thread_num}: {file.name}')
                time.sleep(0.1)
            except:
                # Если не получилось скачать файл
                print('.', end='')
                time.sleep(3)


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
