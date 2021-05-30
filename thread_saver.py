import dvach
import time
import os

DELAY = 5
SAVE_MEDIA = True
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
            print(f"Удаленный пост: {post.num}")


if __name__ == '__main__':
    print('Введите название доски: ', end='')
    board_name = input()
    print('Введите номер треда: ', end='')
    thread_num = input()

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
        try:
            add_new_posts(safe_thread, thread.posts)

            print_deleted_posts(safe_thread, thread.posts)

            safe_thread.save(FOLDER)

            time.sleep(DELAY)

            # Снова скачать тред
            thread = get_thread(board, thread_num)
        except:
            print("Ошибка, повтор")
            time.sleep(5)
