# Формирование html страницы треда

Файлы
* `index.html` - шаблон страницы
* `style.css` - стили для шаблона
* blocks - директория с блоками из шаблона
  * `op_post.html` - вырезка оп-поста из шаблона
  * `post.html` - вырезка поста из шаблона
  * `dashboard.html` - боковая панель с навигацией
  * `script.js` - скрипт для генерации навигации

Во время генерации страницы значения в фигурных скобках заменяются. Это происходит в классе `HtmlGenerator`.
