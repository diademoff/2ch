import json
import re
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup

import dvach


def make_thread(names, displaynames=None):
    """Use the existing posts fixture and real model objects."""
    with open('test_files/posts_json.json', encoding='utf-8') as source:
        data = json.load(source)
    op = data['threads'][0]['posts'][0]
    template = op['files'][0]
    op['files'] = [dict(template, name=name, path='/b/src/' + name,
                        displayname=(displaynames[index] if displaynames is not None else name))
                   for index, name in enumerate(names)]
    thread = dvach.Thread('b')
    thread.get_posts(json.dumps(data))
    thread.num = thread.get_op_post.num
    thread.comment_html = thread.get_op_post.comment_html
    return thread


class OfflineTestCase(unittest.TestCase):
    def setUp(self):
        network = patch('dvach.requests.get', side_effect=AssertionError('Real HTTP forbidden'))
        self.http = network.start()
        self.addCleanup(network.stop)

    def assert_local_urls(self, html_path, names, selector='.op_post_file'):
        soup = BeautifulSoup(html_path.read_text(encoding='utf-8'), 'html.parser')
        items = soup.select(selector)
        self.assertEqual(len(items), len(names))
        for item, name in zip(items, names):
            for element in item.select('[href], [src]'):
                url = element.get('href', element.get('src'))
                self.assertTrue(url.startswith('./'))
                parsed = urlsplit(url)
                self.assertEqual((parsed.scheme, parsed.netloc, parsed.query, parsed.fragment),
                                 ('', '', '', ''))
                resolved = urlsplit(urljoin(html_path.as_uri(), url))
                self.assertEqual(Path(unquote(resolved.path)), html_path.parent / name)
                self.assertTrue(Path(unquote(resolved.path)).is_file())
        return soup


class TestOpPostFiles(OfflineTestCase):
    def test_mixed_attachments_in_order(self):
        names = ['a.jpg', 'b.png', 'c.jpeg', 'd.gif', 'e.webp', 'f.mp4', 'g.webm', 'h.pdf']
        thread = make_thread(names)
        soup = BeautifulSoup(dvach.HtmlGenerator.get_thread_htmlpage(thread), 'html.parser')
        items = soup.select('.op_post_file')
        self.assertEqual([item.a['href'] for item in items], ['./' + name for name in names])
        for index, (item, name) in enumerate(zip(items, names)):
            with self.subTest(name=name):
                self.assertEqual(item.find_all('a')[-1]['href'], './' + name)
                self.assertEqual(len(item.select('a')), 1)
                self.assertEqual(item.get_text(), name if index >= 5 else '')
                self.assertEqual(len(item.select('img')), int(index < 5))
                self.assertEqual(len(item.select('video')), int(index in (5, 6)))
                if index < 5:
                    self.assertEqual(item.img.parent['href'], item.img['src'])
                    self.assertNotIn('width', item.img.attrs)
                    self.assertNotIn('height', item.img.attrs)
                if index in (5, 6):
                    self.assertIn('controls', item.video.attrs)
                    self.assertEqual(item.video['preload'], 'none')
                    self.assertNotIn('autoplay', item.video.attrs)
                    self.assertEqual(item.video['src'], './' + name)
                    self.assertIsNone(item.video.find_parent('a'))
                    self.assertEqual(item.video.find_next_sibling(), item.a)
                    self.assertEqual(item.a['href'], item.video['src'])
        self.http.assert_not_called()

    def test_only_video_and_other_files_can_be_saved(self):
        thread = make_thread(['clip.webm', 'archive.zip', 'README'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(thread.save(folder))
            soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
        self.assertEqual(len(soup.select('.op_post_file')), 3)
        self.assertEqual(len(soup.select('.op_post video')), 1)
        self.assertEqual(len(soup.select('.op_post img')), 0)
        self.http.assert_not_called()

    def test_empty_and_single_image_keep_op_content(self):
        for names in ([], ['one.png']):
            with self.subTest(names=names), tempfile.TemporaryDirectory() as folder:
                thread = make_thread(names)
                path = Path(thread.save(folder))
                self.assertEqual(path.name, 'thread_' + thread.num + '.html')
                soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
                op = soup.select_one('.op_post')
                self.assertEqual(op.select_one('.op_post_header_time').text.strip(), thread.get_op_post.date)
                self.assertEqual(op.select_one('.op_post_header_num').text.strip(), '№' + thread.num)
                self.assertEqual(op.select_one('.op_post_msg').text.strip(), thread.comment_html)
                self.assertEqual(len(op.select('img')), len(names))
                self.assertEqual(len(op.select('.op_post_file')), len(names))
                self.assertFalse(op.select('[src=""], [href=""]'))
                if not names:
                    self.assertIsNone(op.select_one('.op_post_files'))

    def test_special_names_classification_and_local_url_resolution(self):
        names = ['many.dots.JPG', 'photo.JPEG', 'photo.PNG', 'photo.GIF', 'photo.WEBP',
                 'movie.MP4', 'movie.WEBM', 'README', 'image.jpg.txt',
                 'a b"&\'#%.png', 'javascript:example.pdf', 'имя файла.pdf',
                 'видео "&\'#%.MP4']
        labels = ['<img src=x onerror="bad"> & "quoted" {msg}'] + [''] * (len(names) - 2) + [
            '<script>bad</script> & "quoted" {msg} {images} {num}']
        thread = make_thread(names, labels)
        thread.posts[1].files = list(thread.get_op_post.files)
        with tempfile.TemporaryDirectory() as folder:
            for name in names:
                (Path(folder) / name).write_bytes(b'local attachment')
            soup = self.assert_local_urls(Path(thread.save(folder)), names)
            self.assert_local_urls(Path(folder) / ('thread_' + thread.num + '.html'), names, '.post_file')
        items = soup.select('.op_post_file, .post_file')
        self.assertEqual(items[0].img['alt'], labels[0])
        for index, item in enumerate(items):
            index %= len(names)
            with self.subTest(name=names[index]):
                self.assertEqual(len(item.select('img')), int(index in (0, 1, 2, 3, 4, 9)))
                self.assertEqual(len(item.select('video')), int(index in (5, 6, 12)))
                self.assertEqual(len(item.select('a')), 1)
                expected_text = '' if item.select('img') else labels[index] or names[index]
                self.assertEqual(item.a.text, expected_text)
                for element in item.find_all(True):
                    self.assertFalse(set(element.attrs) - {'href', 'src', 'alt', 'controls', 'preload', 'target'})
                if item.video:
                    self.assertEqual(item.video['src'], item.a['href'])
        self.assertFalse(soup.select('.op_post_files script, .op_post_files [onerror], .post_files script, .post_files [onerror]'))

    def test_legacy_arguments_do_not_limit_files(self):
        thread = make_thread(['a.jpg', 'b.png', 'c.mp4'])
        for render in (dvach.HtmlGenerator.get_thread_htmlpage, dvach.HtmlGenerator.get_op_post_htmlpage):
            with self.subTest(render=render.__name__):
                self.assertEqual(render(thread), render(thread, 'obsolete-first-image.jpg'))
                self.assertEqual(len(BeautifulSoup(render(thread), 'html.parser').select('.op_post_file')), 3)

    def test_placeholder_like_content_is_not_replaced(self):
        label = '{msg} {files} {num} {date}'
        thread = make_thread(['{msg}.png'], [label])
        thread.comment_html = 'Literal {files} and {msg} in OP text'
        thread.posts[1].files = list(thread.get_op_post.files)
        thread.posts[1].comment_html = 'Literal {images} {answers} {msg} {num} in reply'
        soup = BeautifulSoup(dvach.HtmlGenerator.get_thread_htmlpage(thread), 'html.parser')
        self.assertEqual(soup.select_one('.op_post_msg').text.strip(), thread.comment_html)
        self.assertEqual(len(soup.select('.op_post_file')), 1)
        item = soup.select_one('.op_post_file')
        self.assertEqual(item.a.text, '')
        self.assertEqual(item.img['alt'], label)
        self.assertEqual(unquote(item.img['src']), './{msg}.png')
        reply = soup.select_one('.post')
        self.assertEqual(reply.select_one('.post_msg').text.strip(), thread.posts[1].comment_html)
        self.assertEqual(reply.img['alt'], label)
        self.assertEqual(unquote(reply.img['src']), './{msg}.png')

    def test_ordinary_posts_keep_existing_markup_and_order(self):
        thread = make_thread(['op.webp'])
        post = thread.posts[1]
        template = thread.get_op_post.files[0]
        post.files = [dvach.Post_file(dict(vars(template), name=name))
                      for name in ['reply.jpg', 'reply.png', 'reply.webm']]
        files = BeautifulSoup(dvach.HtmlGenerator.get_post_files(post), 'html.parser')
        self.assertEqual(len(files.select('.post_file')), 3)
        self.assertEqual([img.parent['target'] for img in files.select('img')], ['_blank', '_blank'])
        soup = BeautifulSoup(dvach.HtmlGenerator.get_thread_htmlpage(thread), 'html.parser')
        ordinary = soup.select('.post')
        self.assertEqual(len(ordinary), len(thread.posts) - 1)
        for order, (element, post) in enumerate(zip(ordinary, thread.posts[1:]), 2):
            self.assertEqual(element['id'], 'post_' + post.num)
            self.assertEqual(element.select_one('.post_header_num').text.strip(), '№' + post.num)
            self.assertEqual(element.select_one('.post_header_order').text.strip(), str(order))
            self.assertEqual(element.select_one('.post_header_time').text.strip(), post.date)
            expected_msg = BeautifulSoup(post.comment_html, 'html.parser')
            self.assertEqual(element.select_one('.post_msg').decode_contents().strip(), str(expected_msg).strip())
            self.assertEqual(str(element), str(BeautifulSoup(
                dvach.HtmlGenerator.get_post_htmlpage(post, order), 'html.parser').div))
        self.assertEqual([img['src'] for img in ordinary[0].select('img')], ['./reply.jpg', './reply.png'])
        self.assertEqual(len(ordinary[0].select('video')), 1)
        self.assertFalse(ordinary[0].select('.op_post_file'))

    def assert_attachment_contract(self, soup, names):
        for selector in ('.op_post_file', '.post_file'):
            items = soup.select(selector)
            self.assertEqual(len(items), len(names))
            for item, name in zip(items, names):
                with self.subTest(selector=selector, name=name):
                    self.assertEqual(len(item.select('a')), 1)
                    self.assertEqual(unquote(item.a['href']), './' + name)
                    extension = Path(name).suffix.lower()
                    if extension in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
                        self.assertEqual([child.name for child in item.find_all(recursive=False)], ['a'])
                        self.assertEqual(item.a.text, '')
                        self.assertEqual(item.img.parent, item.a)
                        self.assertEqual(item.img['src'], item.a['href'])
                        self.assertIsNone(item.video)
                    elif extension in {'.mp4', '.webm'}:
                        self.assertEqual([child.name for child in item.find_all(recursive=False)], ['video', 'a'])
                        self.assertEqual(item.video.find_next_sibling(), item.a)
                        self.assertIsNone(item.video.find_parent('a'))
                        self.assertIn('controls', item.video.attrs)
                        self.assertEqual(item.video['preload'], 'none')
                        self.assertNotIn('autoplay', item.video.attrs)
                        self.assertEqual(item.video['src'], item.a['href'])
                        self.assertEqual(item.a.text, name)
                    else:
                        self.assertFalse(item.select('img, video'))
                        self.assertEqual(item.a.text, name)

    def assert_attachment_css(self, soup):
        # Check declarations AND selector applicability, not browser layout.
        rules = [(selectors.strip(), dict(re.findall(r'([\w-]+)\s*:\s*([^;]+);', body)))
                 for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', soup.style.string)]
        for selector in ('.op_post_file', '.post_file'):
            for item in soup.select(selector):
                declarations = {}
                for css_selector, values in rules:
                    if any(element is item for element in soup.select(css_selector)):
                        declarations.update(values)
                self.assertEqual(declarations.get('display'), 'flex')
                self.assertEqual(declarations.get('flex-direction'), 'column')
        for image in soup.select('.post_file img'):
            declarations = {}
            for css_selector, values in rules:
                if any(element is image for element in soup.select(css_selector)):
                    declarations.update(values)
            self.assertEqual(declarations.get('max-height'), '70px')

    def test_full_and_saved_page_attachment_matrix_and_css(self):
        matrices = [
            ['a.jpg', 'many.dots.JPEG', 'c.PNG', 'd.GIF', 'e.WEBP',
             'f.MP4', 'many.dots.WEBM', 'h.pdf', 'i.zip', 'README', 'image.jpg.txt'],
            [], ['only.mp4', 'only.WEBM'], ['only.zip', 'README']]
        for names in matrices:
            with self.subTest(names=names), tempfile.TemporaryDirectory() as folder:
                thread = make_thread(names)
                # Only OP and first reply have files; all other posts remain present.
                for post in thread.posts[1:]:
                    post.files = []
                thread.posts[1].files = list(thread.get_op_post.files)
                for html in (dvach.HtmlGenerator.get_thread_htmlpage(thread, 'obsolete.jpg'),
                             Path(thread.save(folder)).read_text(encoding='utf-8')):
                    soup = BeautifulSoup(html, 'html.parser')
                    self.assert_attachment_contract(soup, names)
                    self.assert_attachment_css(soup)
                    self.assertEqual(len(soup.select('.post')), len(thread.posts) - 1)
                    self.assertFalse(soup.select('[src=""], [href=""]'))
                    if not names:
                        self.assertFalse(soup.select('.op_post_files, .post_files, img, video'))
                self.assertEqual(list(Path(folder).iterdir()), [Path(folder) / ('thread_' + thread.num + '.html')])
        self.http.assert_not_called()

    def test_save_validation_errors_are_preserved(self):
        thread = make_thread([])
        with tempfile.TemporaryDirectory() as folder:
            file_path = Path(folder) / 'not-a-directory'
            file_path.write_text('existing data', encoding='utf-8')
            with self.assertRaisesRegex(Exception, 'Вы указали файл, но требуется директория'):
                thread.save(str(file_path))
            self.assertEqual(file_path.read_text(encoding='utf-8'), 'existing data')
            thread.posts = []
            with self.assertRaisesRegex(Exception, 'Посты не скачаны'):
                thread.save(folder)


if __name__ == '__main__':
    unittest.main()
