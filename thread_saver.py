import dvach
import time
import os
import sys

DELAY = 15
SAVE_MEDIA = True
global FOLDER
FOLDER = "saver"


def get_board(board_name: str) -> dvach.Board:
    while True:
        try:
            board = dvach.Board.from_json(
                dvach.Board.json_download(board_name))
            board.update_threads()
            return board
        except:
            print("Не удалось подключиться, повтор")
            time.sleep(5)


def get_thread(board, thread_num):
    while True:
        if thread_num not in list(board.threads.keys()):
            raise Exception('Тред не существует')
        try:
            thread = board.threads[thread_num]
            thread.update_posts()
            return thread
        except:
            print("Не удалось получить тред, повтор")
            time.sleep(5)


def is_post_in_list(post: dvach.Post, posts_list):
    for i in posts_list:
        if i.num == post.num:
            return True
    return False


def save_post_files(post: dvach.Post):
    for f in post.files:
        path = os.path.normpath(f"{FOLDER}/{f.name}")
        if os.path.exists(path):
            print(f"Файл {f.name} существует")
            continue
        f.save(path)
        print(f"Скачан файл: {f.name}")


def add_new_posts(safe_thread: dvach.Thread, posts):
    for post in posts:
        if not is_post_in_list(post, safe_thread.posts):
            safe_thread.posts.append(post)
            print(f'Новый пост: {post.num}')
            if SAVE_MEDIA:
                save_post_files(post)


def print_deleted_posts(safe_thread: dvach.Thread, posts):
    for post in safe_thread.posts:
        if not is_post_in_list(post, posts):
            if post.num not in deleted_posts:
                print(f"Удаленный пост: {post.num}")
                deleted_posts.append(post.num)


def get_input():
    """Скрипт можно запустить, передав параметры из консоли.

    Параметры:
        1 - название доски
        2 - номер треда
        3 (не обязательный) - имя папки

    Returns:
        board_name, thread_num
    """
    if len(sys.argv) >= 1:
        # Первый аргумент это название файла, он не нужен
        sys.argv = sys.argv[1:]

    if len(sys.argv) == 0:
        print('Введите название доски: ', end='')
        board_name = input()
        print('Введите номер треда: ', end='')
        thread_num = input()
        return (board_name, thread_num)

    if len(sys.argv) >= 2:
        return (sys.argv[0], sys.argv[1])
    else:
        raise Exception("Переданны не корректные параметры")


deleted_posts = []
if __name__ == '__main__':
    board_name, thread_num = get_input()

    if len(sys.argv) >= 3:
        FOLDER = sys.argv[2]

    if not os.path.exists(FOLDER):
        os.mkdir(FOLDER)

    board = get_board(board_name)

    # Скаченный тред с двача
    thread = get_thread(board, thread_num)

    # Локальный тред на диске
    # Так как тред это ссылочный тип
    # Скопированы самые важные поля
    safe_thread = dvach.Thread(board_name)
    safe_thread.lasthit = thread.lasthit
    safe_thread.num = thread.num
    safe_thread.comment_html = thread.comment_html

    while True:
        add_new_posts(safe_thread, thread.posts)

        print_deleted_posts(safe_thread, thread.posts)

        safe_thread.save(FOLDER)

        time.sleep(DELAY)

        try:
            # Снова скачать тред
            thread = get_thread(board, thread_num)
        except:
            print("Ошибка, повтор")
            time.sleep(5)
