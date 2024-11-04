import re
import cv2
import numpy as np
from pytesseract import pytesseract, image_to_string

# Tesseract-OCR ning joylashuvini Linux tizimida ko'rsatish
pytesseract.tesseract_cmd = '/usr/bin/tesseract'  # Tesseract o'rnatilgan yo'l

# Rasmingizni yuklash
def to_str(file) -> str:
    nparr = np.frombuffer(file, np.uint8)
    # NumPy massividan rasmni dekodlash
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    lower = np.array([0, 0, 0], dtype=np.uint8)
    upper = np.array([50, 50, 50], dtype=np.uint8)

    # Rasmni BGR dan HSV ga o'girish
    image = cv2.threshold(image, 190, 250, cv2.THRESH_BINARY)[1]
    # cv2.imshow("awdwd", image)  # Agar rasmni ko'rmoqchi bo'lsangiz, bu qatorni yoqing
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # Oq ranglarni tanlash
    mask = cv2.inRange(hsv_image, lower, upper)

    # Oq ranglar ustida konturlarni aniqlash
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Har bir konturni aylantirish
    for contour in contours:
        # Konturlarni kvadratga aylantirish
        x, y, w, h = cv2.boundingRect(contour)
        if w < 3 and h < 3:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

    # Matnni aniqlash
    text = image_to_string(image, config='--psm 6 outputbase digits')

    # Aniqlangan matnni qaytarish
    return re.sub(r'\D', '', text)
# print(to_str(open("./capcha.jpg", "rb").read()))