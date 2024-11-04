from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle
from kivy.lang import Builder
from database import DatabaseConnection
import requests
from datetime import datetime
from threading import Thread
from kivy.clock import Clock
from functools import partial
from utils import get_last_seven_days
import kundalikcom_func
import os
from android.permissions import request_permissions, Permission
request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

Builder.load_file("Login.kv")
Builder.load_file("Home.kv")
Builder.load_file("Datas.kv")
Builder.load_file("Let.kv")



# O'chiriladi
######################################
from kivy.core.window import Window
Window.size = (400, 600)
######################################

class ActivePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.separator_height = 0

class NoActivePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.separator_height = 0
    def set(self, matn):
        self.ids.matn.text = matn


class AddPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.separator_height = 0
    def tekshirish(self):
        login = self.ids.login.text
        password = self.ids.password.text
        how, data = kundalikcom_func.login_user(login, password)
        if how:
            self.ids.tugma.color = (0,1,0,1)
        else:
            self.ids.tugma.color = (1,0,0,1)
    def add_func(self):
        try:
            name = self.ids.name.text.strip()
            login = self.ids.login.text.strip()
            password = self.ids.password.text.strip()
            if app.database.logins_len() >= 70:
                app.show_error("Limit to'ldi", "Afsuski ayni paytda dastur faqat 70 tagacha foydalanuvchini boshqara oladi!")
            elif name == "":
                app.show_error("Ism ni kiriting", "Ismi kiritish maydoni bo'sh bo'lishi mumkin emas")
            elif " " in login or login == "":
                app.show_error("Login xato kiritildi", "Bunday login bo'lishi mumkin emas.\nQayta kiriting")
            elif " " in password or password == "":
                app.show_error("Parol xato kiritildi", "Bunday parol bo'lishi mumkin emas.\nQayta kiriting")
            else:
                app.database.add_login(name, login, password)
                Clock.schedule_once(lambda dt: app.root.DatasPage.get_datas())
                self.dismiss()
        except:
            app.show_error("Mavjud login kiritldi", "Ushbu login bilan boshqa foydalanuvchi mavdud")

class EditPopup(Popup):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.data = data
        self.separator_height = 0
        self.ids.name.text = data["name"]
        self.ids.login.text = data["login"]
        self.ids.password.text = data["password"]
    def tekshirish(self):
        login = self.ids.login.text
        password = self.ids.password.text
        print(login, password)
    def save_func(self):
        name = self.ids.name.text.strip()
        password = self.ids.password.text.strip()
        if name == "":
            app.show_error("Ism ni kiriting", "Ismi kiritish maydoni bo'sh bo'lishi mumkin emas")
            self.ids.name.text = self.data["name"]
            self.ids.password.text = self.data["password"]
        elif " " in password or password == "":
            app.show_error("Parol xato kiritildi", "Bunday parol bo'lishi mumkin emas.\nQayta kiriting")
            self.ids.name.text = self.data["name"]
            self.ids.password.text = self.data["password"]
        else:
            app.database.set_login(self.data["id"], name, self.data["login"], password, 1)
            Clock.schedule_once(lambda dt: app.root.DatasPage.get_datas())
            self.dismiss()
    def del_func(self):
        app.database.delete_login(self.data["id"])
        Clock.schedule_once(lambda dt: app.root.DatasPage.get_datas())
        self.dismiss()

class MessagePopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = ""
        self.separator_height = 0
    def set(self, title, text, button):
        self.ids.title.text = title
        self.ids.text.text = text
        if button is not None:
            self.ids.tugma.text = button
        self.open()
    def button_func(self):
        pass

class ErrorPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "0"
        self.separator_height = 0
    def set(self, title, text, button):
        self.ids.title.text = title
        self.ids.text.text = text
        if button is not None:
            self.ids.tugma.text = button
        self.open()
    def button_func(self):
        pass


class DatasLoginContent1(BoxLayout):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.ids.name.text = data["name"]
        self.ids.mall.text = f'login: {data["login"]}\nparol: {data["password"]}'
        self.edit_page = EditPopup(data)
    def edit_func(self):
        self.edit_page.open()

class DatasLoginContent2(BoxLayout):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.ids.name.text = data["name"]
        self.ids.mall.text = f'login: {data["login"]}\nparol: {data["password"]}'
        self.edit_page = EditPopup(data)
    def edit_func(self):
        self.edit_page.open()



class HomeContent1(BoxLayout):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.ids.sana.text = data["sana"]
        self.ids.sana_foiz.text = str(data["foiz"])+"%"
        self.ids.sana_data.text = f'Jami: {data["all_num"]} ta hisob\nKirilgan: {int(data["all_num"]) - int(data["err_num"])} ta hisob\nParoli xatolar: {data["err_num"]} ta'

class HomeContent2(BoxLayout):
    def __init__(self, data, **kwargs):
        super().__init__(**kwargs)
        self.ids.sana.text = data["sana"]
        self.ids.sana_foiz.text = str(data["foiz"])+"%"
        self.ids.sana_data.text = f'Jami: {data["all_num"]} ta hisob\nKirilgan: {int(data["all_num"]) - int(data["err_num"])} ta hisob\nParoli xatolar: {data["err_num"]} ta'

class LoginScreen(Screen):
    def get_login_code(self, username, password):
        try:
            res = requests.post("https://api.projectsplatform.uz/accounts/login", json={"username": username, "password": password})
            import webbrowser
            from functools import partial
            if "detail" in res.json():
                app.show_error("Xatolik", f"Username yoki parol xato")
            else:
                app.show_message("Telgram bilan tasdiqlash", f"Telegram botimizdan kelgan 6 xonali kod ni kirting", "Kodni ochish",partial(webbrowser.open,f"https://t.me/projectsplatformbot"))
        except requests.ConnectionError:
            app.show_error("Internetga ulanmagansiz", "Qurilmangizni  internet tarmog'iga ulang!", "qayta urinish", partial(self.get_login_code, username, password), True)
        except:
            app.show_error("Xatolik", f"Nimadir xato ketdi qayta urinib ko'ring")
    def login_func(self, username, password, code):
        try:
            res = requests.post("https://api.projectsplatform.uz/accounts/check-login-code", json={"username": username, "password": password, "code": int(code)})
            app.database.set_data("token", res.json()["token"])
            app.root.current = "home"
            app.database.set_datas(self.get_full_data(res.json()["token"]))
            app.data_population()
        except:
            pass
    def get_full_data(self, token):
        try:
            res = requests.post("https://api.projectsplatform.uz/accounts/about_account", json={"token": token})
            return res.json()
        except requests.ConnectionError:
            app.show_error("Internetga ulanmagansiz", "Qurilmangizni  internet tarmog'iga ulang!", "qayta urinish", app.data_population, True)
        return dict()
    def logout(self):
        app.database.logout()
        app.root.current = "login"

class HomeScreen(Screen):
    def __init__(self, **r):
        super().__init__(**r)
        self.show_message = app.show_message
    # Login qilib chiqish
    def all_logins_run(self):
        all_logins, erros_logins = app.database.get_logins()
        n=0
        num = len(all_logins)
        for login in all_logins.keys():
            password = all_logins[login]["password"]
            how, _ = kundalikcom_func.login_user(login, password)
            app.database.set_login(all_logins[login]["id"], how)
            self.ids.today_foiz.text = f"{100*n//num}%"
            self.ids.today_qism.text = f"{n}/{num}"
            n+=how
        self.ids.today_foiz.text = f"{100*n//num}%"
        self.ids.today_qism.text = f"{n}/{num}"
        app.database.set_data("last", datetime.now().strftime('%d.%m.%Y'))
        # malumot: sana|foiz|all_num|err_num
        app.database.set_data(datetime.now().strftime('%d.%m'), f"{datetime.now().strftime('%d.%m.%Y')}|{100*n//num}|{num}|{num-n}")

    def contents_refresh(self):
        all_days = get_last_seven_days()
        n=0
        self.ids.contents_box.clear_widgets()
        for kun in all_days:
            kun_data = app.database.get_data(kun)
            if kun_data is not None:
                # malumot: sana|foiz|all_num|err_num
                sana, foiz, all_num, err_num = map(str, kun_data.split("|"))
                if n%2 == 0:
                    content = HomeContent1({
                        "foiz": foiz,
                        "sana": sana,
                        "all_num": all_num,
                        "err_num": err_num
                    })
                else:
                    content = HomeContent2({
                        "foiz": foiz,
                        "sana": sana,
                        "all_num": all_num,
                        "err_num": err_num
                    })
                self.ids.contents_box.add_widget(content)
                n+=1
        self.ids.contents_box.height = n*150

    def set_datas(self, text, rang):
        self.ids.letsenziya_label.text = text
        self.ids.letsenziya_label.color = rang
        fullname = app.database.get_data("full_name")
        balance = app.database.get_data("balance")
        if fullname != None:
            if len(fullname) >= 13:
                fullname = fullname[:10]+"..."
            self.ids.fullname.text = fullname
        else:
            app.root.manager.current = "login"
        if balance is not None:
            if balance[0] == "-" or balance[0] == "0":
                app.root.LetsenziyaPage.ids.balance_label.color = (1,0,0,1)
                app.root.LetsenziyaPage.ids.balance_label.text = f"{int(balance):,} so'm"
            else:
                app.root.LetsenziyaPage.ids.balance_label.color = (1,1,1,1)
                app.root.LetsenziyaPage.ids.balance_label.text = f"{int(balance):,} so'm"
        self.ids.letsenziya_label.color = rang

class DatasScreen(Screen):
    def set_container(self, content_name):
        if content_name == "all":
            self.ids.datas_all_button.canvas.before.clear()
            with self.ids.datas_all_button.canvas.before:
                Color(0.4667, 0.2392, 0.7922, 1.0)
                RoundedRectangle(pos=(self.ids.datas_all_button.pos[0] + 5, self.ids.datas_all_button.pos[1] + 5), size=(self.ids.datas_all_button.size[0]-10,self.ids.datas_all_button.size[1]-10), radius=[18])
            self.ids.datas_err_button.canvas.before.clear()
            with self.ids.datas_err_button.canvas.before:
                Color(0.1490, 0.0000, 1.0000, 0.21)
                RoundedRectangle(pos=(self.ids.datas_err_button.pos[0] + 5, self.ids.datas_err_button.pos[1] + 5), size=(self.ids.datas_err_button.size[0]-10,self.ids.datas_err_button.size[1]-10), radius=[18])
        else:
            self.ids.datas_all_button.canvas.before.clear()
            with self.ids.datas_all_button.canvas.before:
                Color(0.1490, 0.0000, 1.0000, 0.21)
                RoundedRectangle(pos=(self.ids.datas_all_button.pos[0] + 5, self.ids.datas_all_button.pos[1] + 5), size=(self.ids.datas_all_button.size[0]-10,self.ids.datas_all_button.size[1]-10), radius=[18])

            self.ids.datas_err_button.canvas.before.clear()
            with self.ids.datas_err_button.canvas.before:
                Color(0.4667, 0.2392, 0.7922, 1.0)
                RoundedRectangle(pos=(self.ids.datas_err_button.pos[0] + 5, self.ids.datas_err_button.pos[1] + 5), size=(self.ids.datas_err_button.size[0]-10,self.ids.datas_err_button.size[1]-10), radius=[18])

    def set_datas(self, text, rang):
        self.ids.letsenziya_label.text = text
        self.ids.letsenziya_label.color = rang
        fullname = app.database.get_data("full_name")
        if fullname != None:
            if len(fullname) >= 13:
                fullname = fullname[:10]+"..."
            self.ids.fullname.text = fullname
        else:
            app.root.manager.current = "login"
    
    def get_datas(self):
        all_logins, err_logins = app.database.get_logins()
        self.ids.all_number.text = f"Jami: {len(all_logins)}"
        self.ids.err_number.text = f"Paroli xatolar: {len(err_logins)}"
        self.ids['all_page'].clear_widgets()
        self.ids.all_page.height = len(all_logins)*100
        n=0
        for login in all_logins.keys():
            data = all_logins[login]
            if n%2==0:
                self.ids.all_page.add_widget(DatasLoginContent1(data))
            else:
                self.ids.all_page.add_widget(DatasLoginContent2(data))
            n+=1
        self.ids['err_page'].clear_widgets()
        self.ids.err_page.height = len(err_logins)*100
        n=0
        for login in err_logins.keys():
            data = err_logins[login]
            if n%2==0:
                self.ids.err_page.add_widget(DatasLoginContent1(data))
            else:
                self.ids.err_page.add_widget(DatasLoginContent2(data))
            n+=1

    def show_add_page(self):
        add_popup = AddPopup()
        add_popup.open()

class LetsenziyaScreen(Screen):
    def set_datas(self, text, rang):
        self.ids.letsenziya_label.text = text
        self.ids.letsenziya_label.color = rang
        fullname = app.database.get_data("full_name")
        if fullname != None:
            if len(fullname) >= 13:
                fullname = fullname[:10]+"..."
            self.ids.fullname.text = fullname
        else:
            app.root.manager.current = "login"
    def get_narx(self, months_count):
        return requests.post("https://api.projectsplatform.uz/kundalikcom/price_months_mobile", json={
            "months_count": months_count
        }).json()
    def get_narx_in_database(self, months_count):
        if months_count >= 3:
            return int(app.database.get_data("chegirma_oy_price"))*(months_count-(months_count//12)*3)
        else:
            return int(app.database.get_data("oy_price"))*months_count
    def oy_add(self):
        try:
            value = int(self.ids.oy_input.text[:-3])+1
            self.ids.oy_input.text = f"{value} oy"
            self.ids.oy_all_price.text = f"Jami: {self.get_narx_in_database(value):,} so'm"
        except:
            pass
    def oy_rm(self):
        if True:
            value = max(int(self.ids.oy_input.text[:-3])-1, 0)
            self.ids.oy_input.text = f"{value} oy"
            self.ids.oy_all_price.text = f"Jami: {self.get_narx_in_database(value):,} so'm"
        else:
            pass
    def oy_buy(self):
        try:
            if int(self.ids.oy_input.text[:-3]):
                res = requests.post("https://api.projectsplatform.uz/kundalikcom/buy_api_mobile", json={
                    "token": app.database.get_data("token"),
                    "months_count": int(self.ids.oy_input.text[:-3])
                })
                if res.json()["how"]:
                    ActivePopup().open()
                else:
                    popup = NoActivePopup()
                    popup.set(res.json()["message"])
                    popup.open()
        except requests.ConnectionError:
            self.show_error("Internetga ulanmagansiz", "Qurilmangizni  internet tarmog'iga ulang!", "qayta urinish", b_func = self.data_population)
        except:
            pass
    def yil_add(self):
        try:
            # yil sonini oshiramiz
            value = int(self.ids.yil_input.text[:-4]) + 1
            self.ids.yil_input.text = f"{value} yil"
            self.ids.yil_all_price.text = f"Jami: {self.get_narx_in_database(value * 12):,} so'm"  # 12 oy = 1 yil hisobiga
        except:
            pass

    def yil_rm(self):
        if True:
            # yil sonini kamaytirib, minimal qiymatni 0 qilib qo'yamiz
            value = max(int(self.ids.yil_input.text[:-4]) - 1, 0)
            self.ids.yil_input.text = f"{value} yil"
            self.ids.yil_all_price.text = f"Jami: {self.get_narx_in_database(value * 12):,} so'm"  # 12 oy = 1 yil hisobiga
        else:
            pass

    def yil_buy(self):
        try:
            # faqat yil soni 0 dan katta bo'lsa davom etadi
            if int(self.ids.yil_input.text[:-4]):
                res = requests.post("https://api.projectsplatform.uz/kundalikcom/buy_api_mobile", json={
                    "token": app.database.get_data("token"),
                    "months_count": int(self.ids.yil_input.text[:-4]) * 12  # yillarni oyga aylantirish
                })
                if res.json()["how"]:
                    ActivePopup().open()
                else:
                    popup = NoActivePopup()
                    popup.set(res.json()["message"])
                    popup.open()
        except requests.ConnectionError:
            self.show_error("Internetga ulanmagansiz", "Qurilmangizni internet tarmog'iga ulang!", "qayta urinish", b_func=self.data_population)
        except:
            pass

class RootWidget(ScreenManager):
    # Ekranlarni `ScreenManager` ichida yaratish
    def __init__(self, page_name, **kwargs):
        super().__init__(**kwargs)
        self.LoginPage = LoginScreen(name="login")
        self.add_widget(self.LoginPage)
        self.HomePage = HomeScreen(name="home")
        self.add_widget(self.HomePage)
        self.LetsenziyaPage = LetsenziyaScreen(name="letsenziya")
        self.add_widget(self.LetsenziyaPage)
        self.DatasPage = DatasScreen(name="datas")
        self.add_widget(self.DatasPage)
        self.transition.direction = 'up'
        self.current = page_name

class KundalikCOMApp(App):
    def build(self):
        self.database = DatabaseConnection()
        token = self.database.get_data("token")
        if token:
            self.root = RootWidget(page_name="home")
            
            Clock.schedule_once(lambda dt: self.data_population())
        else:
            self.root = RootWidget(page_name="login")
        return self.root
    def data_population(self):
        try:
            self.database.set_datas(self.root.LoginPage.get_full_data(self.database.get_data("token")))
            res = requests.post("https://api.projectsplatform.uz/kundalikcom/check_mobile", json={"token": self.database.get_data("token"), "device_id": self.database.get_data("device_id")})
            if not res.json()["how"]:
                self.root.current = "login"
                self.show_error("Ikkinchi qurilma", res.json()["message"])
                return
            self.letsenziya_data(res.json())
            today = self.database.get_data(datetime.now().strftime('%d.%m'))
            data = {
                "oy_price": str(self.root.LetsenziyaPage.get_narx(1)),
                "chegirma_oy_price": str(self.root.LetsenziyaPage.get_narx(3)//3)
            }
            self.database.set_datas(data)
            self.root.LetsenziyaPage.ids.yillik_label.text = f'Yillik oling va 12 oy emas 9 oylikni\nnarxida {9*int(data["chegirma_oy_price"]):,} so\'mdan'
            self.root.LetsenziyaPage.ids.oylik_label.text = f'1 oylik {int(data["oy_price"]):,} so’m, 3 yoki 3+ oy\n-20% chegirma bilan oyiga {int(data["chegirma_oy_price"]):,}'

            if self.database.get_data("last") == datetime.now().strftime('%d.%m.%Y') and today is not None:
                self.root.HomePage.ids.today_foiz.text = today.split("|")[1]+"%"
                self.root.HomePage.ids.today_qism.text = f'{int(today.split("|")[2]) - int(today.split("|")[3])}/{today.split("|")[2]}'
            else:
                self.root.HomePage.ids.today_foiz.text = "0%"
                self.root.HomePage.ids.today_qism.text = "0/"+str(self.database.logins_len())
            Clock.schedule_once(lambda dt: self.root.HomePage.contents_refresh())
        except requests.ConnectionError:
            self.show_error("Internetga ulanmagansiz", "Qurilmangizni  internet tarmog'iga ulang!", "qayta urinish", b_func = self.data_population)
        except:
            print(res.json())
            self.root.current = "login"
            self.show_error("Xatolik!", "Hisobingizga qayta kiring")
    def letsenziya_data(self, data):
        if 'end_active_date' in data:
            end_date = datetime.fromisoformat(data['end_active_date'])
            # Vaqtni formatlash
            formatted_date = end_date.strftime('%d.%m.%Y')
            if data['size'] > 0:
                rang = (0, 0.231, 0.435, 1)
                text = f"{formatted_date}y"
            else:
                rang = (1, 0, 0, 1)
                text = """letstenziyangiz tugagan"""
                self.show_error("Letsenziya", "Kechirasiz sizning letsenziyangiz tugagan!\nDasturdan foydalanish uchun xarid amalga oshirishingiz kerak!")
                

            Clock.schedule_once(lambda dt: self.root.get_screen('home').set_datas(text, rang))
            Clock.schedule_once(lambda dt: self.root.get_screen('datas').set_datas(text, rang))
            Clock.schedule_once(lambda dt: self.root.get_screen('letsenziya').set_datas(text, rang))
    def show_message(self, title, text, button=None, b_func=None, relase=None):
        if relase is not None:
            popup = MessagePopup(auto_dismiss=relase)
        else:
            popup = MessagePopup()
        if b_func is not None:
            popup.button_func = b_func
        popup.set(title, text, button)
    def show_error(self, title, text, button=None, b_func=None, relase=None, height=None):
        if relase is not None:
            popup = ErrorPopup(auto_dismiss=relase)
        else:
            popup = ErrorPopup()
        if b_func is not None:
            popup.button_func = b_func
        if height is not None:
            popup.button_func = b_func
        popup.set(title, text, button)


if __name__ == '__main__':
    app = KundalikCOMApp()
    app.run()
