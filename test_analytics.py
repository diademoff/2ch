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
        self.assertEqual(b.threads[i].num, "245698531")
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
        self.assertEqual(list(new.keys())[0], "245684546")

        new = b.get_new_threads(threads_withnew_2)
        self.assertEqual(len(new), 2)
        self.assertEqual(list(new.keys())[0], "245684546")
        self.assertEqual(list(new.keys())[1], "695423564")
        