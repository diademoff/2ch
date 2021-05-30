# О проекте
![GitHub repo size](https://img.shields.io/github/repo-size/diademoff/2ch)
![CodeFactor Grade](https://img.shields.io/codefactor/grade/github/diademoff/2ch)
![GitHub](https://img.shields.io/github/license/diademoff/2ch)
![GitHub Repo stars](https://img.shields.io/github/stars/diademoff/2ch?style=social)

Хочешь скачать все файлы с /b или другого раздела? И без дубликатов? И только файлы больше/меньше X Килобайт? Или только картинки/только видео? Или файлы только с конкретного треда? Или тебе нужен трекер, который будет отбирать треды по ключевым словам? *Всё это здесь! И даже больше!*

В репозитории представлен готовый набор скриптов для [двача](https://2ch.hk), все скрипты можно кастомизировать под свои задачи. При минимальных знаниях питона можно с легкостью написать скрипт под свои нужды. Вся информация ниже.

# Установка
[Видеоинструкция](https://drive.google.com/file/d/1LLfW1EWSTYcFTAoCR02h_Ai04-IzOlba/)

Установите [python](https://www.python.org)

Скачайте zip архив или:
```
git clone https://github.com/diademoff/2ch
```

Установите зависимости:
```
cd 2ch
pip install -r requirements.txt
```

Запускайте нужный скрипт:
```
python {название скрипта}.py
```

# Список скриптов
* Скачать все файлы с треда [`media.py`](./media.py)
* Уведомления о новых тредах на досках [`tracker.py`](./tracker.py)
* Самые популярные треды на доске [`popular.py`](./popular.py)
* Скачивать все файлы доски [`board_media.py`](./board_media.py)

# Редактирование скриптов
Все скрипты можно редактировать под ваши задачи.
* `media.py`
  * `FOLDER_NAME = 'media'` - Изменить имя папки, в которую будут сохраняться файлы
* `tracker.py`
  * `text_limit = 155` - Изменить длину строки
  * `board_names = 'b news sex v hw gg dev soc rf ma psy fet'` - Изменить список досок (писать через пробел)
  * `KEY_WORDS` - Указать ключевые слова
* `popular.py`
  * `text_limit = 164` - Длина строки
  * `max_lines = 55` - Максимальное количество строк в выводе
  * `board_name = 'b'` - Доска, которая парсится
  * `KEY_WORDS` - Выводить треды только с ключевыми словами
* `board_media.py`
  * `BOARD = 'b'` - Имя борды, с которой скачивать файлы
  * `FOLDER_NAME = 'media'` - Имя папки, в которую скачивать файлы
  * `KEY_WORDS = []` - Отбирать треды по ключевым словам, если ключевые слова не указаны, то будут скачиваться файлы всех тредов
  * `EXTENSIONS = []` - Файлы с какими расширениями скачивать
  * `MAX_FILE_SIZE` - Задать максимальный размер файла в Килобайтах
  * `MIN_FILE_SIZE` - Задать минимальный размер файла в Килобайтах


# FAQ
* Скрипт не запускается.

Проверьте установлены ли зависимости: `pip install -r requirements.txt`. Проверьте кодировку файлов. Проверьте, что у вас установлена версия Python > 3.

* Как сравниваются изображения?

Изображения сравниваются по содержимому. Даже если у изображений разное расширение `png` и `jpg`, или разный размер они всё равно будут распознаны как одинаковые.

* Ты используешь api двача?

Да. А конкретно:
```
https://2ch.hk/makaba/mobile.fcgi?task=get_thread&board={board_name}&thread={num}&post=1
http://2ch.hk/{name}/threads.json
```
* Зачем тебе beautiful soup?

Преимущественно чтобы убирать html теги в постах. Если в посте **жирный текст**, то получается так:
`<strong>текст</strong>`. Этот тэг нужно убрать, чтобы остался только текст.

* Как указать ключевые слова?

Откройте нужный скрипт и отредактируйте по образцу. Обратите внимание на форматирование, запятые и кавычки.
```py
KEY_WORDS = [
    "цуиь",
    "mp4"
]
```

* Скрипты кроссплатформенные?

Да. Скрипты были проверены на Linux и Windows.

# Для разработчиков
Весь api хранится в файле `dvach.py`. Подключаем:

```py
import dvach
```
## Структура
* **Board**
  * `name: str` - Имя доски
  * `posts: dict` - Список постов, это словарь. Ключ - это номер треда, значение - переменная типа `Thread`
  * `json_link: str` - Ссылка на json тредов
  * `from_json()` - Получить объект `Board` из json'а
  * `json_download()` - Скачать json доски
  * `thread_exists()` - Есть ли на доске тред с указанным номером
  * `update_threads()` - Обновить список тредов на доске
  * `sort_threads_by_score()` - Отсортировать список тредов по очкам, чем ближе элемент к началу списка, тем больше у него очков
  * `get_new_threads()` - Сравнить текущий список тредов с другим и получить словарь новых тредов
  * `get_dead_threads()` - Сравнить текущий список тредов с другим и получить словарь утонувших тредов
* **Thread**
  * `comment: str` - Текст в ОП посте
  * `num: str` - Номер треда
  * `posts_count: int` - Количество постов
  * `score: float` - Сколько очков у треда
  * `subject: str` - Сокращенный `comment`
  * `views: int` - Количество просмотров
  * `unique_posters: int` - Количество уникальных просмотров (появится после обновления постов)
  * `board_name: str` - Какой доске принадлежит тред
  * `posts = []` - Список постов
  * `get_link: str` - Ссылка на тред
  * `json_posts_link: str` - Ссылка на json треда
  * `save(path)` - сохранить в html посты треда в указанную папку
  * `IsOk()` - Подходит ли тред по заданным ключевым словам
  * `update_posts()` - Скачать json и обновить их список, вызывает функцию `get_posts()`
  * `get_posts()` - Спарсить json и обновить `unique_posters` и `posts`
  * `json_download()` - Получить json постов в чистом виде
* **Post**
  * `comment: str` - Текст
  * `num: str` - Номер
  * `files: []` - Список файлов
* **Post_file**
  * `displayname: str` - Отображаемое имя
  * `name: str` - Имя
  * `download_link: str` - Ссылка на скачивание
  * `width: int` - Ширина
  * `height: int` - Высота
  * `size: int` - Размер файла
  * `IsImage: bool` - Является ли файл изображением
  * `IsVideo: bool` - Является ли файл видео
  * `save()` - Сохранить файл по указанному пути
  * `IsOk()` - Подходит ли файл по заданным расширениям, максимальному и минимальному размеру


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

Получить список с номерами тредов:
```py
# Список из номеров тредов, каждый номер имеет строковой тип.
thread_nums = list(board.threads.keys())
```

Отсортируем по популярности и снова получим список номеров тредов:
```py
board.sort_threads_by_score()
thread_nums = list(board.threads.keys())
```

Первый элемент теперь является номером самого популярного треда:
```py
most_popular_num = thread_nums[0]
```

## Треды
Мы получили *номер* самого популярного треда, теперь получим сам тред из словаря `threads`:
```
thread = board.threads[most_popular_num]
```
В этом словаре значение имеет тип `Thread`. Посмотрим тип переменной `thread`:
```py
print(type(thread))
```

Получим: `<class 'dvach.Thread'>`

Получим список постов в треде:
```py
print(f"Количество постов (длина posts): {len(thread.posts)}")
print(f"Количество постов (posts_count): {thread.posts_count}")

thread.update_posts()

print(f"Количество постов (длина posts): {len(thread.posts)}")
print(f"Уникальных просмотров: {thread.unique_posters}")
```

На выходе получим:
```
Количество постов (длина posts): 0
Количество постов (posts_count): 60
Количество постов (длина posts): 64
Уникальных просмотров: 34
```

`unique_posters` - появляется только после вызова `update_posts()` или `get_posts()`.

Получение количества постов с помощью `len(thread.posts)` является точнее, но требует загрузки всех постов, в то время как `thread.posts_count` известно во время *получения тредов на доске*.

## Сохранение треда в html
Для сохранение треда используйте класс `HtmlGenerator` и метод `get_thread_htmlpage`. Этот метод возвращает html код, который можно сохранить в файл.
```py
op_file = thread.posts[0].files[0]  # Картинка в ОП-посте
img_path = os.path.normpath(f'./{op_file.name}')  # Путь, куда мы ее сохраним
op_file.save(img_path)  # Сохраняем картинку

# Получаем html
html = dvach.HtmlGenerator.get_thread_htmlpage(thread, img_path)

# Создаём файл
file = open(f'thread_{thread.num}.html', 'w')

# Записывает туда html страницу
file.write(html)
```

## Посты
После получения списка постов с помощью `update_posts()` в поле `posts` появился список постов начиная с ОП-поста.

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
Теперь получим первый файл в посте, если файл есть:
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
Весь код, используемый в примерах:
```py
import dvach
import os

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

print(f"Количество постов (длина posts): {len(thread.posts)}")
print(f"Уникальных просмотров: {thread.unique_posters}")

op_file = thread.posts[0].files[0]  # Картинка в ОП-посте
img_path = os.path.normpath(f'./{op_file.name}')  # Путь, куда мы ее сохраним
op_file.save(img_path)  # Сохраняем картинку

# Получаем html
html = dvach.HtmlGenerator.get_thread_htmlpage(thread, img_path)

# Создаём файл
file = open(f'thread_{thread.num}.html', 'w')

# Записывает туда html страницу
file.write(html)

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
