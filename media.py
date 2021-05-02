import time
import os
import analytics

# Скачать все файлы с треда

if __name__ == '__main__':
    print('Введите название борды: ', end='')
    board_name = input()
    print('Введите номер треда: ', end='')
    thread_num = input()

    # Скачиваем json борды
    board_json = analytics.Board.json_download(board_name)

    board = analytics.Board.from_json(board_json)

    # Тред с которого скачивать файлы
    thread = board.threads[thread_num]

    # Скачиваем json треда
    json_thread = thread.json_download()

    # Получаем посты
    thread.get_posts(json_thread)

    # Создаём папку с медиа
    if not os.path.exists('media'):
        os.mkdir('media')

    # Скачиваем файлы в папку media
    for post in thread.posts:
        for file in post.files:
            download_path = "media/" + file.name

            if os.path.exists(download_path):
                print(f'Файл {file.name} существует')

            try:
                file.save("media/" + file.name)
                print(f'Скачен файл: {file.name}')
                time.sleep(0.5)
            except:
                print('.', end='')
                time.sleep(3)
