
import flet as ft
import threading
import requests
import json
import ast
import re
import time
import random
import binascii
import os
import uuid
import secrets
import string
from MedoSigner import Argus, Gorgon, Ladon, md5

# ====== دوال جلب البيانات ======
def get_user_id(username):
    """جلب معرف المستخدم من TikTok"""
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Android 10; Pixel 3 Build/QKQ1.200308.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/125.0.6394.70 Mobile Safari/537.36 trill_350402 JsSdk/1.0 NetType/MOBILE Channel=googleplay AppName/trill app_version/35.3.1 ByteLocale/en ByteFullLocale/en Region/IN AppId/1180 Spark/1.5.9.1 AppVersion/35.3.1 BytedanceWebview/d8a21c6"
    }
    try:
        tikinfo = requests.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=10).text
        info = tikinfo.split('webapp.user-detail"')[1].split('"RecommenUserList"')[0]
        user_id = info.split('id":"')[1].split('",')[0]
        return user_id
    except:
        return None

def sign(params, payload: str = None, sec_device_id: str = "", cookie: str or None = None, aid: int = 1233, license_id: int = 1611921764, sdk_version_str: str = "2.3.1.i18n", sdk_version: int = 2, platform: int = 19, unix: int = None):
    """توقيع الطلبات"""
    x_ss_stub = md5(payload.encode('utf-8')).hexdigest() if payload is not None else None
    if not unix:
        unix = int(time.time())
    return Gorgon(params, unix, payload, cookie).get_value() | {
        "x-ladon": Ladon.encrypt(unix, license_id, aid),
        "x-argus": Argus.get_sign(params, x_ss_stub, unix, platform=platform, aid=aid, license_id=license_id, sec_device_id=sec_device_id, sdk_version=sdk_version_str, sdk_version_int=sdk_version)
    }

def get_streaming_level(username):
    """جلب مستوى الدعم للبث المباشر"""
    user_id = get_user_id(username)
    if not user_id:
        return None
    
    url = f"https://webcast16-normal-no1a.tiktokv.eu/webcast/user/?request_from=profile_card_v2&request_from_scene=1&target_uid={user_id}&iid={random.randint(1, 10**19)}&device_id={random.randint(1, 10**19)}&ac=wifi&channel=googleplay&aid=1233&app_name=musical_ly&version_code=300102&version_name=30.1.2&device_platform=android&os=android&ab_version=30.1.2&ssmix=a&device_type=RMX3511&device_brand=realme&language=ar&os_api=33&os_version=13&openudid={binascii.hexlify(os.urandom(8)).decode()}&manifest_version_code=2023001020&resolution=1080*2236&dpi=360&update_version_code=2023001020&_rticket={round(random.uniform(1.2, 1.6) * 100000000) * -1}4632&current_region=IQ&app_type=normal&sys_region=IQ&mcc_mnc=41805&timezone_name=Asia%2FBaghdad&carrier_region_v2=418&residence=IQ&app_language=ar&carrier_region=IQ&ac2=wifi&uoo=0&op_region=IQ&timezone_offset=10800&build_number=30.1.2&host_abi=arm64-v8a&locale=ar&region=IQ&content_language=gu%2C&ts={round(random.uniform(1.2, 1.6) * 100000000) * -1}&cdid={uuid.uuid4()}&webcast_sdk_version=2920&webcast_language=ar&webcast_locale=ar_IQ"
    
    headers = {
        'User-Agent': "com.zhiliaoapp.musically/2023001020 (Linux; U; Android 13; ar; RMX3511; Build/TP1A.220624.014; Cronet/TTNetVersion:06d6a583 2023-04-17 QuicVersion:d298137e 2023-02-13)"
    }
    headers.update(sign(url.split('?')[1], '', "AadCFwpTyztA5j9L" + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(9)), None, 1233))
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        level_match = re.search(r'"default_pattern":"(.*?)"', response.text)
        if level_match:
            level_text = level_match.group(1)
            if 'المستوى رقم' in level_text:
                return int(level_text.split('المستوى رقم ')[1])
        return None
    except:
        return None

def get_user_info_new_api(username: str) -> dict | None:
    """
    استخدام الـ API الجديد المحسن لجلب معلومات المستخدم
    """
    try:
        # الخطوة الأولى: البحث عن المستخدم
        search_url = "https://ttpub.linuxtech.io:5004/api/search"
        search_headers = {
            'Host': "ttpub.linuxtech.io:5004",
            'User-Agent': "Dart/3.5 (dart:io)",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json"
        }
        search_data = {"username": username}
        
        print(f"البحث عن المستخدم: {username}")
        search_res = requests.post(search_url, data=json.dumps(search_data), headers=search_headers, timeout=15)
        print(f"استجابة البحث: {search_res.status_code}")
        
        if search_res.status_code != 200:
            print(f"خطأ في البحث: {search_res.text}")
            return None
            
        search_result = search_res.json()
        print(f"نتيجة البحث: {search_result}")
        
        if 'user' not in search_result or 'sid' not in search_result['user']:
            print("لم يتم العثور على المستخدم أو SID")
            return None
            
        sid = search_result['user']['sid']
        print(f"تم العثور على SID: {sid}")
        
        # الخطوة الثانية: جلب تفاصيل المستخدم باستخدام SID
        detail_url = "https://ttpub.linuxtech.io:5004/api/search_by_sid_build_request"
        detail_data = {"sid": sid, "count_requests": 3}
        
        detail_res = requests.post(detail_url, data=json.dumps(detail_data), headers=search_headers, timeout=15)
        print(f"استجابة التفاصيل: {detail_res.status_code}")
        
        if detail_res.status_code != 200:
            print(f"خطأ في جلب التفاصيل: {detail_res.text}")
            return None
            
        detail_result = detail_res.json()
        print(f"نتيجة التفاصيل: {detail_result}")
        
        if 'request' not in detail_result or len(detail_result['request']) == 0:
            print("لا توجد طلبات متاحة")
            return None
            
        # الخطوة الثالثة: استخدام URL والـ headers للحصول على البيانات النهائية
        final_url = detail_result['request'][0]["url"]
        final_headers = ast.literal_eval(detail_result['request'][0]["headers"])
        
        print(f"الحصول على البيانات النهائية من: {final_url[:100]}...")
        final_res = requests.get(final_url, headers=final_headers, timeout=15)
        print(f"استجابة البيانات النهائية: {final_res.status_code}")
        
        if final_res.status_code != 200:
            print(f"خطأ في جلب البيانات النهائية: {final_res.text}")
            return None
        
        # التحقق من وجود محتوى قبل محاولة تحليل JSON
        if not final_res.text.strip():
            print("الاستجابة فارغة")
            return None
            
        final_data = final_res.json()
        print("تم جلب البيانات بنجاح")
        return final_data
        
    except json.JSONDecodeError as e:
        print(f"خطأ في تحليل JSON: {e}")
        print(f"محتوى الاستجابة: {final_res.text[:500] if 'final_res' in locals() else 'غير متوفر'}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"خطأ في الطلب: {e}")
        return None
    except Exception as e:
        print(f"خطأ غير متوقع: {e}")
        return None


def get_user_info_fallback(username: str) -> dict | None:
    """
    API احتياطي للحصول على معلومات المستخدم
    """
    try:
        # استخدام TikTok API مباشرة
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        response = requests.get(f'https://www.tiktok.com/@{username}', headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        html_content = response.text
        
        # البحث عن بيانات المستخدم في HTML
        try:
            # البحث عن JSON data في الصفحة
            start = html_content.find('webapp.user-detail"')
            if start == -1:
                return None
                
            end = html_content.find('"RecommenUserList"', start)
            if end == -1:
                end = html_content.find('}</script>', start)
                
            if end == -1:
                return None
                
            user_data_str = html_content[start:end]
            
            # استخراج معلومات أساسية
            user_id_match = re.search(r'id":"(\d+)"', user_data_str)
            username_match = re.search(r'uniqueId":"([^"]+)"', user_data_str)
            nickname_match = re.search(r'nickname":"([^"]+)"', user_data_str)
            follower_match = re.search(r'followerCount":(\d+)', user_data_str)
            following_match = re.search(r'followingCount":(\d+)', user_data_str)
            heart_match = re.search(r'heartCount":(\d+)', user_data_str)
            video_match = re.search(r'videoCount":(\d+)', user_data_str)
            signature_match = re.search(r'signature":"([^"]*)"', user_data_str)
            verified_match = re.search(r'verified":(true|false)', user_data_str)
            
            if not user_id_match:
                return None
                
            return {
                'user': {
                    'uid': user_id_match.group(1),
                    'unique_id': username_match.group(1) if username_match else username,
                    'nickname': nickname_match.group(1) if nickname_match else '',
                    'signature': signature_match.group(1) if signature_match else '',
                    'follower_count': int(follower_match.group(1)) if follower_match else 0,
                    'following_count': int(following_match.group(1)) if following_match else 0,
                    'total_favorited': int(heart_match.group(1)) if heart_match else 0,
                    'aweme_count': int(video_match.group(1)) if video_match else 0,
                    'verification_type': 1 if verified_match and verified_match.group(1) == 'true' else 0,
                    'favoriting_count': 0,
                    'account_type': 0,
                    'is_star': False,
                    'is_effect_artist': False,
                    'live_commerce': False,
                    'commerce_user_level': 0,
                    'with_commerce_entry': False,
                    'custom_verify': '',
                    'sec_uid': '',
                    'avatar_medium': {'url_list': []},
                    'share_info': {'share_url': f'https://www.tiktok.com/@{username}'},
                    'original_musician': {'music_count': 0, 'music_used_count': 0},
                    'mplatform_followers_count': 0
                }
            }
            
        except Exception as e:
            print(f"خطأ في تحليل HTML: {e}")
            return None
            
    except Exception as e:
        print(f"خطأ في API الاحتياطي: {e}")
        return None


def format_number(num):
    """تنسيق الأرقام لتكون قابلة للقراءة"""
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    elif num >= 1000:
        return f"{num/1000:.1f}K"
    else:
        return str(num)


# ====== واجهة Flet ======
def app_main(page: ft.Page):
    page.title = "ELBAD_OFF"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#000000"
    page.window.width = 400
    page.window.height = 700
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = "adaptive"

    # ==== الصفحة الأولى (المقدمة) ====
    splash_image = ft.Image(
        src="https://i.postimg.cc/hPH3KXrp/IMG-20250825-000216-706.jpg",
        width=380, height=300, fit=ft.ImageFit.CONTAIN, border_radius=10
    )
    dev_info = ft.Text(
        "𝐓𝐢𝐤𝐭𝐨𝐤      ► elbad_off\n𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 ► elbad_off",
        size=16, weight=ft.FontWeight.BOLD, color="#FFFFFF", text_align=ft.TextAlign.CENTER
    )
    btn_contact = ft.ElevatedButton(
        "مراسلة المبرمج", on_click=lambda e: page.launch_url("https://t.me/elbad_off"),
        width=300, height=50,
        style=ft.ButtonStyle(bgcolor="#303F9F", color="#FFFFFF",
                             shape=ft.RoundedRectangleBorder(radius=10))
    )
    def go_next(_):
        build_main_ui()
    btn_skip = ft.ElevatedButton(
        "تخطي", on_click=go_next, width=300, height=50,
        style=ft.ButtonStyle(bgcolor="#D32F2F", color="#FFFFFF",
                             shape=ft.RoundedRectangleBorder(radius=10))
    )
    page.add(
        ft.Container(
            content=ft.Column([ft.Container(height=30), splash_image, ft.Container(height=20),
                               dev_info, ft.Container(height=30), btn_contact,
                               ft.Container(height=15), btn_skip, ft.Container(height=30)],
                              alignment="center", horizontal_alignment="center", spacing=10),
            padding=20, expand=True
        )
    )

    # ==== الواجهة الأساسية ====
    def build_main_ui():
        page.controls.clear()

        top_image = ft.Image(
            src="https://i.postimg.cc/2SBvfwjX/image.jpg",
            width=220, height=220, fit=ft.ImageFit.CONTAIN
        )
        
        # نص ELBAD المتحرك بألوان مختلفة
        animated_text = ft.Text(
            "ELBAD",
            size=40,
            weight=ft.FontWeight.BOLD,
            color="#FF6B6B",
            text_align=ft.TextAlign.CENTER,
            animate_opacity=ft.animation.Animation(1000, ft.AnimationCurve.EASE_IN_OUT)
        )
        
        # دالة تغيير اللون والتأثير
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF"]
        color_index = [0]  # استخدام قائمة لتمرير المرجع
        animation_running = [True]  # متحكم في إيقاف التحريك
        
        def animate_text():
            import time
            while animation_running[0]:
                try:
                    # تغيير اللون
                    animated_text.color = colors[color_index[0] % len(colors)]
                    color_index[0] += 1
                    
                    # تأثير الاختفاء والظهور
                    animated_text.opacity = 0.3
                    page.update()
                    time.sleep(0.5)
                    
                    if not animation_running[0]:
                        break
                        
                    animated_text.opacity = 1.0
                    page.update()
                    time.sleep(0.5)
                except Exception:
                    break
        
        # بدء التحريك في خيط منفصل
        threading.Thread(target=animate_text, daemon=True).start()
        
        # تحسين مربع إدخال اليوزر
        username_tf = ft.TextField(
            hint_text="ادخل اليوزر",
            width=320,
            height=50,
            text_align=ft.TextAlign.CENTER,
            border_color="#4CAF50",
            focused_border_color="#66BB6A",
            bgcolor="#1A1A1A",
            color="#FFFFFF",
            hint_style=ft.TextStyle(color="#888888"),
            text_style=ft.TextStyle(color="#FFFFFF", size=16),
            border_radius=10,
            content_padding=ft.padding.symmetric(horizontal=15, vertical=10)
        )

        # صندوق النتيجة
        result_text = ft.Text("", color="#FFFFFF", size=12, selectable=True)
        result_box = ft.Container(
            content=ft.Column([result_text], scroll="adaptive"),
            width=350, 
            height=300,
            bgcolor="#111111", 
            border_radius=10, 
            padding=15,
            border=ft.border.all(1, "#333333")
        )

        def fetch_data():
            user = (username_tf.value or "").strip().replace("@", "")
            if not user:
                result_text.value = "⚠️ الرجاء إدخال اليوزر"
                page.update()
                return

            result_text.value = "⏳ جاري جلب البيانات من الـ API الجديد..."
            page.update()

            # جلب البيانات باستخدام الـ API الجديد
            user_data = get_user_info_new_api(user)
            
            # إذا فشل الـ API الأول، جرب الـ API الاحتياطي
            if not user_data:
                result_text.value = "⏳ جاري المحاولة مع API احتياطي..."
                page.update()
                user_data = get_user_info_fallback(user)
            
            if not user_data:
                result_text.value = "❌ فشل في جلب بيانات المستخدم أو المستخدم غير موجود"
                page.update()
                return

            # جلب مستوى الدعم
            result_text.value = "⏳ جاري جلب مستوى الدعم..."
            page.update()
            
            streaming_level = get_streaming_level(user)

            try:
                # استخراج البيانات من الهيكل الصحيح
                if 'user' not in user_data:
                    result_text.value = "❌ خطأ: لا يمكن العثور على بيانات المستخدم"
                    page.update()
                    return
                
                user_info = user_data['user']
                
                # المعلومات الأساسية
                uid = user_info.get('uid', 'غير متوفر')
                username = user_info.get('unique_id', 'غير متوفر')
                nickname = user_info.get('nickname', 'غير متوفر')
                signature = user_info.get('signature', 'لا يوجد')
                sec_uid = user_info.get('sec_uid', 'غير متوفر')
                
                # الإحصائيات
                followers = user_info.get('follower_count', 0)
                following = user_info.get('following_count', 0)
                total_favorited = user_info.get('total_favorited', 0)
                videos = user_info.get('aweme_count', 0)
                favoriting_count = user_info.get('favoriting_count', 0)
                
                # معلومات التحقق والخصوصية
                verification_type = user_info.get('verification_type', 0)
                verified = verification_type > 0
                custom_verify = user_info.get('custom_verify', '')
                
                # معلومات إضافية
                avatar_medium = user_info.get('avatar_medium', {})
                avatar_url = ''
                if avatar_medium and 'url_list' in avatar_medium and avatar_medium['url_list']:
                    avatar_url = avatar_medium['url_list'][0]
                
                # معلومات الحساب
                account_type = user_info.get('account_type', 0)
                is_star = user_info.get('is_star', False)
                is_effect_artist = user_info.get('is_effect_artist', False)
                live_commerce = user_info.get('live_commerce', False)
                
                # معلومات المشاركة
                share_info = user_info.get('share_info', {})
                share_url = share_info.get('share_url', f'https://www.tiktok.com/@{username}')
                
                # معلومات التجارة
                commerce_user_level = user_info.get('commerce_user_level', 0)
                with_commerce_entry = user_info.get('with_commerce_entry', False)
                
                # معلومات الموسيقى
                original_musician = user_info.get('original_musician', {})
                music_count = original_musician.get('music_count', 0)
                music_used_count = original_musician.get('music_used_count', 0)
                
                # معدلات المشاركة
                mplatform_followers = user_info.get('mplatform_followers_count', 0)
                
                # نوع الحساب
                account_type_text = {
                    0: 'عادي',
                    1: 'تجاري', 
                    2: 'منشئ محتوى',
                    3: 'مؤسسة'
                }.get(account_type, 'غير معروف')
                
                # تنسيق النتيجة مع جميع المعلومات المتوفرة
                streaming_level_text = f"🎮 المستوى {streaming_level}" if streaming_level is not None else "❌ غير متوفر"
                
                result_text.value = (
                    "╔══════════════════════════════╗\n"
                    "║           𝚃𝙸𝙺𝚃𝙾𝙺 𝙸𝙽𝙵𝙾           ║\n"
                    "╠══════════════════════════════╣\n"
                    f"║ 𝐍𝐀𝐌𝐄 ➤ {nickname}\n"
                    f"║ 𝐔𝐒𝐄𝐑𝐍𝐀𝐌𝐄 ➤ @{username}\n"
                    f"║ 𝐔𝐈𝐃 ➤ {uid}\n"
                    f"║ 𝐒𝐄𝐂_𝐔𝐈𝐃 ➤ {sec_uid[:25]}...\n"
                    "╠══════════════════════════════╣\n"
                    f"║ 𝐅𝐎𝐋𝐋𝐎𝐖𝐄𝐑𝐒 ➤ {format_number(followers)}\n"
                    f"║ 𝐅𝐎𝐋𝐋𝐎𝐖𝐈𝐍𝐆 ➤ {format_number(following)}\n"
                    f"║ 𝐓𝐎𝐓𝐀𝐋 𝐋𝐈𝐊𝐄𝐒 ➤ {format_number(total_favorited)}\n"
                    f"║ 𝐕𝐈𝐃𝐄𝐎𝐒 ➤ {format_number(videos)}\n"
                    f"║ 𝐅𝐀𝐕𝐎𝐑𝐈𝐓𝐄𝐒 ➤ {format_number(favoriting_count)}\n"
                    "╠══════════════════════════════╣\n"
                    f"║ 𝐕𝐄𝐑𝐈𝐅𝐈𝐄𝐃 ➤ {'✅ نعم' if verified else '❌ لا'}\n"
                    f"║ 𝐀𝐂𝐂𝐎𝐔𝐍𝐓 𝐓𝐘𝐏𝐄 ➤ {account_type_text}\n"
                    f"║ 𝐒𝐓𝐀𝐑 ➤ {'⭐ نعم' if is_star else '❌ لا'}\n"
                    f"║ 𝐄𝐅𝐅𝐄𝐂𝐓 𝐀𝐑𝐓𝐈𝐒𝐓 ➤ {'🎨 نعم' if is_effect_artist else '❌ لا'}\n"
                    "╠══════════════════════════════╣\n"
                    f"║ 𝐒𝐓𝐑𝐄𝐀𝐌 𝐋𝐄𝐕𝐄𝐋 ➤ {streaming_level_text}\n"
                    f"║ 𝐌𝐔𝐒𝐈𝐂 𝐂𝐎𝐔𝐍𝐓 ➤ {format_number(music_count)}\n"
                    f"║ 𝐌𝐔𝐒𝐈𝐂 𝐔𝐒𝐄𝐃 ➤ {format_number(music_used_count)}\n"
                    f"║ 𝐂𝐎𝐌𝐌𝐄𝐑𝐂𝐄 ➤ {'💼 نعم' if with_commerce_entry else '❌ لا'}\n"
                    f"║ 𝐋𝐈𝐕𝐄 𝐂𝐎𝐌𝐌𝐄𝐑𝐂𝐄 ➤ {'🔴 نعم' if live_commerce else '❌ لا'}\n"
                    "╠══════════════════════════════╣\n"
                    f"║ 𝐁𝐈𝐎 ➤ {signature[:30] if signature else 'لا يوجد'}{'...' if len(signature) > 30 else ''}\n"
                    f"║ 𝐕𝐄𝐑𝐈𝐅𝐘 ➤ {custom_verify if custom_verify else 'لا يوجد'}\n"
                    f"║ 𝐔𝐑𝐋 ➤ tiktok.com/@{username}\n"
                    "╚══════════════════════════════╝\n"
                    f"\n🔗 𝐀𝐕𝐀𝐓𝐀𝐑: {avatar_url[:50] if avatar_url else 'غير متوفر'}{'...' if len(avatar_url) > 50 else ''}\n"
                    "\n═══════════ 𝙱𝚈 @𝙴𝙻𝙱𝙰𝙳_𝙾𝙵𝙵 ═══════════"
                )
                
                # تحديث الواجهة بعد نجاح معالجة البيانات
                page.update()
                    
            except Exception as e:
                result_text.value = (
                    f"❌ خطأ في تحليل البيانات: {str(e)}\n\n"
                    "البيانات المستلمة:\n" + 
                    (str(user_data)[:500] + "..." if len(str(user_data)) > 500 else str(user_data))
                )
                page.update()

        def on_start_click(_):
            threading.Thread(target=fetch_data, daemon=True).start()

        start_btn = ft.ElevatedButton(
            "🔍 البحث", on_click=on_start_click, width=220, height=48,
            style=ft.ButtonStyle(
                bgcolor="#4CAF50", 
                color="#FFFFFF",
                shape=ft.RoundedRectangleBorder(radius=10),
                elevation=3
            )
        )

        page.add(
            ft.Column(
                [top_image, animated_text, ft.Container(height=10), username_tf, ft.Container(height=8),
                 start_btn, ft.Container(height=14), result_box],
                alignment="center", horizontal_alignment="center", spacing=10
            )
        )
        page.update()

# تشغيل التطبيق
if __name__ == "__main__":
    # للتطوير - تشغيل كتطبيق ويب
    ft.app(target=app_main, view=ft.AppView.WEB_BROWSER, port=5000, host="0.0.0.0")
    