# Мониторинг доск

from typing import List
import dvach
import time

text_limit = 155  # Длина строки вывода в консоль


def print_new_threads(new_threads: List[dvach.Thread]):
    for thread in new_threads:

        board_name = '{0:5}'.format(thread.board_name)
        comment_formatted = ('{0:' + str(text_limit) + '}').format(thread.comment[:text_limit:])

        print(f"/{board_name} | {comment_formatted} | {thread.get_link}")

        # Если операционная система linux, то можно отправить уведомление
        # os.system(f'notify-send -t 25000 \"/{board_name} {thread.comment}\"')


if __name__ == '__main__':
    board_names = 'b news sex v hw gg dev soc rf ma psy fet'
    boards = []

    # Добавить все доски в общий список
    for board_name in board_names.split(' '):
        board_json = dvach.Board.json_download(board_name)
        boards.append(dvach.Board.from_json(board_json))

        del board_json

    while True:
        # Мониторинг обновлений
        new_threads = []

        # Заполнить список новыми тредами
        for i in range(len(boards)):
            b = boards[i]

            # Скачать доску с новыми тредами
            try:
                board_json = dvach.Board.json_download(b.name)
                updated_board = dvach.Board.from_json(board_json)
            except:
                print('.', end='')
                time.sleep(3)
                continue

            # Сравнить скаченную доску с существующей
            new = b.get_new_threads(updated_board.threads)

            # Добавить все новые треды в общий список
            # Так как это словарь, цикл перебирает ключи
            for key in new.keys():
                new_threads.append(new[key])

            # Заменить старую доску новой, чтобы потом сравнивать с новой
            boards[i].threads = updated_board.threads
            time.sleep(1)

        # Вывести новые треды
        print_new_threads(new_threads)

        # Задержка между обновлениями
        time.sleep(15)
