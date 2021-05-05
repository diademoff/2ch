import dvach
import time

# Ключевые слова. Если список пустой, то отбора тредов не будет.
KEY_WORDS = [
    # "цуиь",
    # "mp4"
]
text_limit = 164  # Длина строки
max_lines = 55  # Ограничить количество строк. Если равен 0, то ограничений нет


def print_threads(threads):
    # Если max_lines = 0, то ограничений нет
    limit = len(threads.keys()) if max_lines == 0 else max_lines

    for key_index in range(0, limit):
        key = list(threads.keys())[key_index]
        thread = threads[key]

        if not thread.IsOk(KEY_WORDS):
            continue

        # Отформатировать строку с информацией о треде и вывести на экран
        comment_formatted = (
            '{0:' + str(text_limit) + '}').format(thread.comment[:text_limit:])
        score_str = '{0:3}'.format(round(thread.score))

        print(f"{score_str} | {comment_formatted} | {thread.get_link}")


if __name__ == '__main__':
    # доска, которую нужно парсить
    board_name = 'b'

    # Инициализация доски с тредами
    board = dvach.Board.from_json(dvach.Board.json_download(board_name))

    while True:
        # Обновление тредов
        try:
            board.update_threads()
        except:
            print('.', end='')
            time.sleep(3)
            continue

        # Сортировка по очкам
        board.sort_threads_by_score()

        # Вывести на экран
        print_threads(board.threads)

        # 15 секунд интервал обновления
        time.sleep(15)
