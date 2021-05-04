from cv2 import imread, resize, cvtColor, threshold, INTER_AREA, COLOR_BGR2GRAY


def are_similar(img1, img2) -> bool:
    """Похожи ли изображения

    Args:
        img1 (str): путь к первому изображению
        img2 (str): путь к второму изображению

    Returns:
        bool: являются ли изображения схожими
    """
    try:
        hash1 = CalcImageHash(img1)
        hash2 = CalcImageHash(img2)
        # Чем меньше число, тем похожей изображения
        similarity = CompareHash(hash1, hash2)

        return similarity < 7
    except:
        # Файл не картинка или другая ошибка
        return False


def CalcImageHash(img):
    """Преобразовать картинку в строку

    Args:
        img (str): путь к изображению

    Returns:
        str: строковое представление картинки
    """
    image = imread(img)  # Прочитаем картинку
    # Уменьшим картинку
    resized = resize(image, (8, 8), interpolation=INTER_AREA)
    # Переведем в черно-белый формат
    gray_image = cvtColor(resized, COLOR_BGR2GRAY)
    avg = gray_image.mean()  # Среднее значение пикселя
    _, threshold_image = threshold(
        gray_image, avg, 255, 0)  # Бинаризация по порогу

    # Рассчитаем хэш
    _hash = ""
    for x in range(8):
        for y in range(8):
            val = threshold_image[x, y]
            if val == 255:
                _hash += "1"
            else:
                _hash += "0"

    return _hash


def CompareHash(hash1, hash2):
    i = 0
    count = 0
    while i < len(hash1):
        if hash1[i] != hash2[i]:
            count = count + 1
        i = i + 1
    return count
