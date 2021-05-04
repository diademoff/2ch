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


def get_better_img(img1: str, img2: str) -> str:
    """Получить изображение с лучшим расширением

    Args:
        img1 (str): Первая картинка
        img2 (str): Вторая картинка

    Returns:
        str: Лучшая картинка
    """
    i1 = imread(img1)
    i2 = imread(img2)
    height1, width1, channels1 = i1.shape
    height2, width2, channels2 = i2.shape

    if width1 > width2:
        return img1
    else:
        return img2
