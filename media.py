import time
import os
import dvach

# Скачать все файлы с треда
FOLDER_NAME = 'media' # название папки, куда будут скачиваться файлы

if __name__ == '__main__':
    print('Введите название борды: ', end='')
    board_name = input()
    print('Введите номер треда: ', end='')
    thread_num = input()

    # Скачиваем борду с тредами
    board = dvach.Board(board_name)
    board.update_threads()

    # Тред с которого скачивать файлы
    thread = board.threads[thread_num]

    # Скачиваем посты треда
    thread.update_posts()

    # Создаём папку с медиа
    if not os.path.exists(FOLDER_NAME):
        os.mkdir(FOLDER_NAME)

    # Скачиваем файлы в папку media
    for post in thread.posts:
        for file in post.files:
            download_path = os.path.normpath(FOLDER_NAME + '/' + file.name)

            if os.path.exists(download_path):
                print(f'Файл {file.name} существует')
                continue

            try:
                file.save(download_path)
                print(f'Скачен файл: {file.name}')
                time.sleep(0.5)
            except:
                print('.', end='')
                time.sleep(3)
