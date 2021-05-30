# Формирование html страницы треда

Файлы
* `index.html` - шаблон страницы
* `style.css` - стили для шаблона
* blocks - директория с блоками из шаблона
  * `head.html` - head из файла шаблона
  * `op_post.html` - вырезка оп-поста из шаблона
  * `post.html` - вырезка поста из шаблона
  * `answer.html` - вырезка ответов на пост из шаблона

Во время генерации страницы значения в фигурных скобках заменяются. Это происходит в классе `HtmlGenerator`.

Упрощенно это выглядит так:
```py
def get_head():
    return open('blocks/head.html').read()


def get_op():
    return open('blocks/op_post.html').read()


def get_post():
    # get_answers()
    return open('blocks/post.html').read()


code = f"""
<!DOCTYPE html>
<html lang="ru">
{get_head()}
<body>
    <div class="container">
    {get_op()}
    {get_post()}
    </div>
</body>
</html>
"""

open('output.html', 'w').write(code)
```