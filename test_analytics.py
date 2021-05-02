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
