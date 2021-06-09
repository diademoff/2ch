import unittest
import dvach
import filecompare
import os


class TestAnalytics(unittest.TestCase):

    def read_file(self, file_name) -> str:
        """Прочитать файл в директории test_files/

        В директории `test_files/` собраны файлы которые используются для тестирования

        Args:
            file_name (str): название файла в директории test_files/

        Returns:
            str: Содержимое файла
        """
        f = open(os.path.normpath(f'test_files/{file_name}'))
        text = f.read()
        f.close()
        return text

    def test_read_json(self):
        """Тест парсинга json доски
        """
        json_plain = self.read_file('threads_json.json')

        # Тест этой функции
        b = dvach.Board.from_json(json_plain)

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
        """Тест обнаружения новых тредов на доске
        """
        json_plain = self.read_file('threads_json.json')
        b = dvach.Board.from_json(json_plain)

        json_withnew_plain = self.read_file('threads_json_withnew.json')
        threads_withnew_1 = dvach.Board.from_json(json_withnew_plain).threads

        json_withnew2_plain = self.read_file('threads_json_withnew2.json')
        threads_withnew_2 = dvach.Board.from_json(json_withnew2_plain).threads

        # Тест если добавляется один тред
        new = b.get_new_threads(threads_withnew_1)
        self.assertEqual(len(new), 1)
        self.assertEqual(list(new.keys())[0], "6")

        # Тест если добавляется два треда
        new = b.get_new_threads(threads_withnew_2)
        self.assertEqual(len(new), 2)
        self.assertEqual(list(new.keys())[0], "6")
        self.assertEqual(list(new.keys())[1], "7")

    def test_dead_thread(self):
        """Тест обнаружения умерших тредов на доске
        """
        json_plain = self.read_file('threads_json.json')
        b = dvach.Board.from_json(json_plain)

        json_deleted_plain = self.read_file('threads_json_removed.json')
        threads_deleted_1 = dvach.Board.from_json(json_deleted_plain).threads

        json_deleted_plain2 = self.read_file('threads_json_removed2.json')
        threads_deleted_2 = dvach.Board.from_json(json_deleted_plain2).threads

        # Тест если удаляется один тред
        deleted = b.get_dead_threads(threads_deleted_1)
        self.assertEqual(len(deleted), 1)
        self.assertEqual(list(deleted.keys())[0], "3")

        # Тест если удаляется два треда
        deleted = b.get_dead_threads(threads_deleted_2)
        self.assertEqual(len(deleted), 2)
        self.assertEqual(list(deleted.keys())[0], "2")
        self.assertEqual(list(deleted.keys())[1], "3")

    def test_read_posts(self):
        """Тест парсига постов в треде по json
        """
        json_plain = self.read_file('posts_json.json')

        thread = dvach.Thread('b')
        # Тест этой функции
        thread.get_posts(json_plain)

        self.assertEqual(thread.unique_posters, 43)
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

    def test_similar_img(self):
        """Тест поиска похожих изображений
        """
        # Эти фото отличаются размером
        file1_1 = os.path.normpath('test_files/images/img1_1.jpg')
        file1_2 = os.path.normpath('test_files/images/img1_2.jpg')
        r1 = filecompare.are_similar(file1_1, file1_2)

        # Эти фото различаются незначительными деталями, но они не одинаковые
        file2_1 = os.path.normpath('test_files/images/img2_1.png')
        file2_2 = os.path.normpath('test_files/images/img2_2.png')
        r2 = filecompare.are_similar(file2_1, file2_2)

        # Эти фото значительно отличаются
        file3_1 = os.path.normpath('test_files/images/img3_1.jpg')
        file3_2 = os.path.normpath('test_files/images/img3_2.jpg')
        r3 = filecompare.are_similar(file3_1, file3_2)

        self.assertEqual(r1, True)
        self.assertEqual(r2, False)
        self.assertEqual(r3, False)

    def test_better_img(self):
        """Тест поиска лучшего изображения из двух
        """
        # Первая картинка лучше
        file1 = os.path.normpath('test_files/images/img1_1.jpg')
        file2 = os.path.normpath('test_files/images/img1_2.jpg')

        best = filecompare.get_better_img(file1, file2)

        self.assertEqual(best, file1)

    def test_isOk(self):
        json_plain = self.read_file('threads_json.json')
        b = dvach.Board.from_json(json_plain)
        thread_num = list(b.threads.keys())[0]
        thread = b.threads[thread_num]

        self.assertEqual(thread.IsOk([]), True)
        self.assertEqual(thread.IsOk(["зумер"]), True)
        self.assertEqual(thread.IsOk(["продолжаем"]), True)
        self.assertEqual(thread.IsOk(["зумеры"]), False)
