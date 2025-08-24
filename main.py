import flet as ft
import webbrowser

def main(page: ft.Page):
    page.title = "Telegram Links"
    page.vertical_alignment = "center"   # وسط الصفحة

    # أزرار مع الروابط
    btn1 = ft.ElevatedButton(
        "WOODE", 
        width=200,
        on_click=lambda e: webbrowser.open("https://t.me/c249c")
    )
    btn2 = ft.ElevatedButton(
        "AL-QANA", 
        width=200,
        on_click=lambda e: webbrowser.open("https://t.me/NO_BRAK")
    )
    btn3 = ft.ElevatedButton(
        "CHAT", 
        width=200,
        on_click=lambda e: webbrowser.open("https://t.me/v249ve")
    )

    page.add(
        ft.Text("Choose a Telegram link:", size=22, weight="bold"),
        btn1,
        btn2,
        btn3
    )

# لتشغيل كتطبيق سطح مكتب
ft.app(target=main)

# لو عايز يشتغل من المتصفح بدل النافذة، استخدم:
# ft.app(target=main, view=ft.WEB_BROWSER)
