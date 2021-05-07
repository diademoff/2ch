import dvach
import imagecompare
from typing import List
import time
import os


# Скачать все файлы со всех тредов доски
BOARD = 'b'
FOLDER_NAME = 'media'  # название папки, куда будут скачиваться файлы
KEY_WORDS = [  # список ключевых слов
    # "WEBM",
    # "webm",
    # "цуиь"
]
EXTENSIONS = [
    'png',
    'jpg',
    'webm',
    'mp4'
]

# Задать максимальный размер файла в Килобайтах
# Если равен 0, то ограничений нет
MAX_FILE_SIZE = 0

# Задать минимальный размер файла в Килобайтах
# Если равен 0, то ограничений нет
MIN_FILE_SIZE = 0


class Hashtable:
    """Файл с информацией об уже скачанных картинках
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
            f = open(self.path, 'a')
            f.write(f'{hash}|{path}\n')
            f.close()
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


class FileDownloadInfo:
    Succeed = 0
    Exists = 1
    IsNotOk = 2
    LinkCreated = 3
    Error = 4


class BoardMedia:
    hashtable: Hashtable
    download_folder: str

    def __init__(self, path_to_folder: str) -> None:
        self.download_folder = path_to_folder
        self.hashtable = Hashtable(
            os.path.normpath(f'{path_to_folder}/hashtable'))

    def findInTable(self, hash: str):
        """Найти такую-же фотографию в базе

        Args:
            hash (str): строковое представление фото

        Returns:
            str: путь к такой же фотографии, если дубликата нет - пустая строка
        """
        if hash in self.hashtable.table.keys():
            return str(self.hashtable.table[hash]).strip()
        else:
            return ''

    def download_file(self, thread_num: str, file: dvach.Post_file):
        """Скачать файл и вернуть информацию о результате

        Args:
            thread_num (str): Номер треда
            file (dvach.Post_file): Файл

        Returns:
            int: FileDownloadInfo
        """
        thread_folder = os.path.normpath(
            f'{self.download_folder}/{thread_num}')
        download_path = os.path.normpath(f'{thread_folder}/' + file.name)

        # Создаём папку с media
        if not os.path.exists(self.download_folder):
            os.mkdir(self.download_folder)
        # Создаём папку треда в media
        if not os.path.exists(thread_folder):
            os.mkdir(thread_folder)

        if os.path.exists(download_path):
            return FileDownloadInfo.Exists

        # Проверяем подходит ли файл
        if not file.IsOk(EXTENSIONS, MAX_FILE_SIZE, MIN_FILE_SIZE):
            return FileDownloadInfo.IsNotOk

        try:
            file.save(download_path)

            if file.IsImage:
                image_hash = imagecompare.CalcImageHash(download_path)
                same_photo = self.findInTable(image_hash)
                if same_photo != '':
                    os.remove(download_path)
                    os.symlink(os.path.abspath(same_photo),
                               download_path, target_is_directory=False)
                    return FileDownloadInfo.LinkCreated
                self.hashtable.add_image(
                    download_path, imagecompare.CalcImageHash(download_path))

            return FileDownloadInfo.Succeed
        except:
            # Если не получилось скачать файл
            return FileDownloadInfo.Error


def download_thread_files(posts: List[dvach.Post], thread_num: str):
    """Скачать файлы постов треда

    Args:
        posts (List[dvach.Post]): список постов
    """
    thread_text = ''
    for post in posts:
        thread_text += f"[{post.num}] {post.comment}\n\n"
        for file in post.files:
            i = boardmedia.download_file(thread_num, file)

            if i == FileDownloadInfo.Succeed:
                print(f'Скачан файл из треда {thread_num}: {file.name}')
            elif i == FileDownloadInfo.Exists:
                # Файл существует
                pass
            elif i == FileDownloadInfo.IsNotOk:
                # Файл не подошел по критериям отбора
                pass
            elif i == FileDownloadInfo.LinkCreated:
                # Ссылка создана
                print(f'Создана ссылка в {thread_num}: {file.name}')
            elif i == FileDownloadInfo.Error:
                print('.', end='')
                time.sleep(3)

            time.sleep(0.1)
    f = open(os.path.normpath(f'{FOLDER_NAME}/{thread_num}/index.txt'), 'w', encoding='utf-8')
    f.write(thread_text)
    f.close()


if __name__ == '__main__':
    # Создаём папку с медиа
    if not os.path.exists(FOLDER_NAME):
        os.mkdir(FOLDER_NAME)

    print('Загрузка файла')
    global boardmedia
    boardmedia = BoardMedia(FOLDER_NAME)

    # Скачиваем доску с тредами
    board = dvach.Board(BOARD)
    while True:
        try:
            board.update_threads()
        except:
            # Если не получилось скачать список тредов
            time.sleep(3)
            continue

        for thread_num in board.threads.keys():
            # Тред с которого скачивать файлы
            thread = board.threads[thread_num]

            if not thread.IsOk(KEY_WORDS):
                continue  # Если не подходит - пропускаем

            # Скачиваем посты треда
            try:
                thread.update_posts()
            except:
                # Если не получислось скачать список постов
                print('.', end='')
                time.sleep(3)
                continue

            # Скачиваем файлы в папку media/{thread_num}
            download_thread_files(thread.posts, thread.num)
