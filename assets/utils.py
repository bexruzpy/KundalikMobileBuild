from datetime import datetime, timedelta

def get_last_seven_days():
    # Hozirgi sanani olish
    today = datetime.now()
    # Oxirgi 7 kun uchun ro'yxat
    last_seven_days = []

    for i in range(7):
        # Hozirgi sanadan i kun oldingi sanani hisoblash
        date = today - timedelta(days=i)
        # Sanani "DD.MM" formatida o'zgartirish
        formatted_date = date.strftime("%d.%m")
        last_seven_days.append(formatted_date)

    return last_seven_days
# print(get_last_seven_days())