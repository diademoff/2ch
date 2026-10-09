from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from bs4 import BeautifulSoup

import dvach
import thread_saver
from test_op_post_files import OfflineTestCase, make_thread


class TestThreadSaver(OfflineTestCase):
    def test_all_downloaded_attachments_resolve_next_to_html(self):
        names = ['one.jpg', 'two.png', 'clip.mp4', 'clip.webm', 'notes & #.pdf']
        downloaded = make_thread(names)
        safe = make_thread([])
        safe.posts = []
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(thread_saver, 'FOLDER', folder), \
                patch.object(thread_saver, 'SAVE_MEDIA', True):
            self.http.side_effect = None
            self.http.return_value = SimpleNamespace(content=b'offline attachment')
            thread_saver.add_new_posts(safe, downloaded.posts[:1])
            path = Path(safe.save(folder))
            self.assertEqual(path.parent, Path(folder))
            self.assert_local_urls(path, names)
            for name in names:
                self.assertEqual((path.parent / name).read_bytes(), b'offline attachment')
            self.assertEqual([call.args[0] for call in self.http.call_args_list],
                             [file.download_link for file in downloaded.get_op_post.files])

    def test_save_media_false_renders_without_download_or_local_files(self):
        names = ['image.jpg', 'clip.webm', 'README']
        downloaded = make_thread(names)
        safe = make_thread([])
        safe.posts = []
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(thread_saver, 'FOLDER', folder), \
                patch.object(thread_saver, 'SAVE_MEDIA', False), \
                patch.object(thread_saver, 'save_post_files', side_effect=AssertionError('Download forbidden')) as save_files:
            thread_saver.add_new_posts(safe, downloaded.posts[:1])
            path = Path(safe.save(folder))
            soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
            self.assertEqual([item.a['href'] for item in soup.select('.op_post_file')],
                             ['./' + name for name in names])
            self.assertEqual(list(Path(folder).iterdir()), [path])
            save_files.assert_not_called()
            self.http.assert_not_called()

    def test_media_failure_does_not_prevent_attachment_links(self):
        downloaded = make_thread(['image.jpg', 'clip.mp4'])
        safe = make_thread([])
        safe.posts = []
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(thread_saver, 'FOLDER', folder), \
                patch.object(thread_saver, 'SAVE_MEDIA', True), \
                patch('dvach.download_link', side_effect=OSError('Offline download failed')):
            thread_saver.add_new_posts(safe, downloaded.posts[:1])
            path = Path(safe.save(folder))
            soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
            self.assertEqual(len(soup.select('.op_post_file')), 2)
            self.assertEqual(list(Path(folder).iterdir()), [path])
        self.http.assert_not_called()


if __name__ == '__main__':
    unittest.main()
