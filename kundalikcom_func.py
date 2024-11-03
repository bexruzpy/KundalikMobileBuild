import requests
from bs4 import BeautifulSoup
import render_capcha_image
from urllib.parse import unquote




def login_user(login, password):
    browser = requests.session()
    try:
        r = browser.post(
            "https://login.emaktab.uz/",
            {"exceededAttempts": "False", "login": login, "password": password},
        )
        soup = BeautifulSoup(r.content, "html.parser")
        if "Chiqish" in soup.get_text():
            user_id = soup.find(title="Sozlamalar").get("href").split("user=")[-1].strip()
            
            return True, ""
        else:
            if soup.find_all(class_="message")[0].get_text().strip() == "Parol yoki login notoʻgʻri koʻrsatilgan. Qaytadan urinib koʻring.":
                return False, "Login yoki parol xato"
            else:
                while True:
                    try:
                        capcha_id = unquote(r.cookies.get('sst')).split("|")[0]
                        url = f"https://login.emaktab.uz/captcha/True/{capcha_id}"
                        file = requests.get(url).content
                        kod = render_capcha_image.to_str(file)
                        r = browser.post(
                            "https://login.emaktab.uz/",
                            {"exceededAttempts": "True", "login": login, "password": password, "Captcha.Input": kod, "Captcha.Id": capcha_id},
                        )
                        soup = BeautifulSoup(r.content, "html.parser")
                        if "Chiqish" in soup.get_text():
                            user_id = soup.find(title="Sozlamalar").get("href").split("user=")[-1].strip()
                            return True, ""
                        elif soup.find_all(class_="message")[0].get_text().strip() == "Parol yoki login notoʻgʻri koʻrsatilgan. Qaytadan urinib koʻring.":
                            return False, "Login yoki parol xato"
                    except requests.exceptions.ConnectionError:
                        return False, "Internega ulanib bo'lmadi"
                    except:
                        return False, "Profilaktika"
    except requests.exceptions.ConnectionError:
        return False, "Internega ulanib bo'lmadi"
    except:
        return False, "Nimadur xato ketdi qayta urining"

