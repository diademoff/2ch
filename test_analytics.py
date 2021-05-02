import unittest
import analytics


class TestAnalytics(unittest.TestCase):

    def read_file(self, file_name) -> str:
        f = open(f'test_files/{file_name}')
        text = f.read()
        f.close()
        return text

    def test_read_json(self):
        json_plain = self.read_file('threads_json.json')
        b = analytics.Board.json_read_data(json_plain)
        
        self.assertEqual(b.name, 'b')
        self.assertEqual(len(b.threads.keys()), 5)

        # Проверка правильности первого треда
        id_of_first = list(b.threads.keys())[0]
        i = id_of_first
        self.assertEqual(b.threads[i].board_name, 'b')
        self.assertEqual(b.threads[i].comment, 'Продолжаем наблюдать за тупорылостью зумерков')
        self.assertEqual(b.threads[i].lasthit, 1619954786)
        self.assertEqual(b.threads[i].num, "1")
        self.assertEqual(b.threads[i].posts_count, 54)
        self.assertEqual(b.threads[i].score, 0)
        self.assertEqual(b.threads[i].subject, "Продолжаем наблюдать за тупорылостью зумерков")
        self.assertEqual(b.threads[i].timestamp, 1619952370)
        self.assertEqual(b.threads[i].views, 0)

    def test_new_thread(self):
        json_plain = self.read_file('threads_json.json')
        b = analytics.Board.json_read_data(json_plain)

        json_withnew_plain = self.read_file('threads_json_withnew.json')
        threads_withnew_1 = analytics.Board.json_read_data(json_withnew_plain).threads

        json_withnew2_plain = self.read_file('threads_json_withnew2.json')
        threads_withnew_2 = analytics.Board.json_read_data(json_withnew2_plain).threads

        new = b.get_new_threads(threads_withnew_1)
        self.assertEqual(len(new), 1)
        self.assertEqual(list(new.keys())[0], "6")

        new = b.get_new_threads(threads_withnew_2)
        self.assertEqual(len(new), 2)
        self.assertEqual(list(new.keys())[0], "6")
        self.assertEqual(list(new.keys())[1], "7")
    
    def test_dead_thread(self):
        json_plain = self.read_file('threads_json.json')
        b = analytics.Board.json_read_data(json_plain)

        json_deleted_plain = self.read_file('threads_json_removed.json')
        threads_deleted_1 = analytics.Board.json_read_data(json_deleted_plain).threads

        json_deleted_plain2 = self.read_file('threads_json_removed2.json')
        threads_deleted_2 = analytics.Board.json_read_data(json_deleted_plain2).threads

        deleted = b.get_dead_threads(threads_deleted_1)
        self.assertEqual(len(deleted), 1)
        self.assertEqual(list(deleted.keys())[0], "3")

        deleted = b.get_dead_threads(threads_deleted_2)
        self.assertEqual(len(deleted), 2)
        self.assertEqual(list(deleted.keys())[0], "2")
        self.assertEqual(list(deleted.keys())[1], "3")

    def test_read_posts(self):
        json_plain = self.read_file('posts_json.json')

        thread = analytics.Thread('b')
        thread.get_posts(json_plain)

        self.assertEqual(len(thread.posts), 7)
        self.assertEqual(len(thread.posts[0].files), 1)

        # Проверка правильности первого поста.
        self.assertEqual(thread.posts[0].comment, "О чём говорить с тней на свидании? Помоги, двач, умоляю.")
        self.assertEqual(thread.posts[0].num, "245701589")
        self.assertEqual(thread.posts[0].files[0].displayname, "3741000.jpg")
        self.assertEqual(thread.posts[0].files[0].name, "16199547970060.jpg")
        self.assertEqual(thread.posts[0].files[0].path, "/b/src/245701589/16199547970060.jpg")
        self.assertEqual(thread.posts[0].files[0].width, 1000)
        self.assertEqual(thread.posts[0].files[0].height, 666)

