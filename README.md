В этом репозитории представлен api [двача](https://2ch.hk) на питоне.

# Использование
Весь api хранится в файле `dvach.py`. Подключаем:

```py
import dvach
```

## Доски
Класс `Board` позволяет взаимодействовать с досками (b, news, po, soc и т.д).

Объявление:
```py
board = dvach.Board('b')
```

Теперь в переменной `board` хранится доска `b`, но там нет никакой информации, кроме названия доски. *Чтобы получить список тредов на доске*:

```py
board.update_threads()
```

Теперь в поле `threads` находится словарь с тредами. Ключ - это номер треда, значение - это тред (`Thread`).

Получить список с номерами тредов
```py
# Список из номеров тредов, каждый номер имеет строковой тип.
thread_nums = list(board.threads.keys()) 
```

Отсортируем по популярности с снова получим список номеров тредов
```py
board.sort_threads_by_score()
thread_nums = list(board.threads.keys())
```

Первый элемент теперь - это номер самого популярного треда.

```py
most_popular_num = thread_nums[0]
```

## Треды
Мы получили номер самого популярного треда, теперь получим сам тред из словаря `threads`. В этом словаре значение имеет тип `Thread`
```
thread = board.threads[most_popular_num]
```
Посмотрим тип переменной `thread`

```py
print(type(thread))
```

Получим: `<class 'dvach.Thread'>`

Поля класса `Thread`:
* `comment: str` - Текст в ОП посте
* `lasthit: int`
* `num: str` - Номер треда
* `posts_count: int` - Количество постов
* `score: float` - Сколько очков у треда
* `subject: str` - Сокращенный `comment`
* `timestamp: int`
* `views: int` - Количество просмотров
* `unique_posters: int` - Количество уникальных просмотров (появится после обновления постов)
* `board_name: str` - какой доске принадлежит тред
* `posts = []` - список постов

Получим список постов в треде
```py
print(f"Количество постов (длина posts): {len(thread.posts)}")
print(f"Количество постов (posts_count): {thread.posts_count}")

thread.update_posts()

print(f"Количество постов (длина posts):{len(thread.posts)}")
print(f"Уникальных просмотров:{thread.unique_posters}")
```

На выходе получим:
```
Количество постов (длина posts): 0
Количество постов (posts_count): 60
Количество постов (длина posts):64
Уникальных просмотров:34
```

`unique_posters` - появляется только после вызова `update_posts()` или `get_posts()`.

Получение количества постов с помощью `len(thread.posts)` является точнее, но требует загрузки всех всех постов, в то время как `thread.posts_count` известно во время получения *получения тредов на доске*.

## Посты
После получения списка постов с помощью `update_posts()` в поле `posts` появился список постов начиная с ОП-поста.

Поля класса `Post`:
* `comment: str` - Текст
* `num: str` - Номер
* `files: []` - Список файлов

Посмотрим второй пост в треде:
```py
post = thread.posts[1]

print(f"Номер: {post.num}")
print(f"Текст: {post.comment}")
print(f"Количество файлов: {len(post.files)}")
```

На выходе получаем:
```
Номер: 210762237
Текст: Бамп
Количество файлов: 1
```

## Файлы
Теперь получим первый файл в посте, если файл есть.
```py
if len(post.files) > 0:
    file = post.files[0]
    print(type(file))
```

На выходе получим: `<class 'dvach.Post_file'>`

Посмотрим больше информации о файле:
```py
print(f"Имя файла: {file.name}")
print(f"Ширина: {file.width}")
print(f"Высота: {file.height}")
print(f"Отображаемое имя: {file.displayname}")
print(f"Ссылка: {file.download_link}")
```

На выходе:
```
Имя файла: 16200245064090.jpg
Ширина: 3118
Высота: 1754
Отображаемое имя: 1620024504280.jpg
Ссылка: https://2ch.hk/b/src/245763818/16200245064090.jpg
```

Можно легко сохранить файл:
```py
file.save(file.name)
```

Файл будет сохранен в директорию в которой выполняется скрипт с именем `16200245064090.jpg`

Можно указать кастомный путь: 
```py
file.save(f"/home/username/{file.name}")
```

## Итого
Весь код, используемый в примерах
```py
import dvach

# Объявить доску
board = dvach.Board('b')

# Скачать треды
board.update_threads()

# Получить список номеров тредов
thread_nums = list(board.threads.keys())

# Отсортировать по очкам
board.sort_threads_by_score()

# Обновить список с номерами тредов
thread_nums = list(board.threads.keys())

# Номер самого популярного треда
most_popular_num = thread_nums[0]

# Самый популярный тред
thread = board.threads[most_popular_num]

# Посмотреть тип переменной
print(type(thread))

print(f"Количество постов (длина posts): {len(thread.posts)}")
print(f"Количество постов (posts_count): {thread.posts_count}")

# Скачать посты
thread.update_posts()

print(f"Количество постов (длина posts):{len(thread.posts)}")
print(f"Уникальных просмотров:{thread.unique_posters}")

# Получить второй пост (который сразу после ОП-поста)
post = thread.posts[1]

print(f"Номер: {post.num}")
print(f"Текст: {post.comment}")
print(f"Количество файлов: {len(post.files)}")

if len(post.files) > 0:
    # Получить первый файл
    file = post.files[0]
    print(type(file))

    print(f"Имя файла: {file.name}")
    print(f"Ширина: {file.width}")
    print(f"Высота: {file.height}")
    print(f"Отображаемое имя: {file.displayname}")
    print(f"Ссылка: {file.download_link}")

    # Сохранить файл
    file.save(file.name)
    # file.save(f"/home/username/{file.name}")
```