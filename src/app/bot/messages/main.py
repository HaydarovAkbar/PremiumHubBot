class MessageText:
    prem_photo_id = 'AgACAgIAAxkBAAESbGxoJutPJGvObgTC_0-ZJHPzD8d7jwACXusxG7W5OUnJSYqm0M8XugEAAwIAA3gAAzYE'
    star_photo_id = 'AgACAgIAAxkBAAESbHZoJuvuDPAyRiReDwOBV1mZg5exzAACbesxG7W5OUlezgnq4SAbPgEAAwIAA3gAAzYE'
    channel_boost_id = 'AgACAgIAAxkBAAESbHtoJuwSLQ1Yxw6AOUS1LekbdgABxMwAAm7rMRu1uTlJNpNuG7vK9ZQBAAMCAAN4AAM2BA'
    manual_video_id = 'BAACAgIAAxkBAAESbH1oJuwsTs_AkrlDBsAiUvCoQpIutgAC8HAAAiTXOUqF5oF6DK9MxTYE'
    gift_photo_id = 'AgACAgIAAxkBAAEULRJoU-LoXnfBiFDdg0ty9JNP27JIQgACnPAxGwE_oUpaHlzctlRYTQEAAwIAA3kAAzYE'
    my_profile_id = 'AgACAgIAAxkBAAEULRtoU-MzwQ7beZ0C5efXN1XSRrTo2wACwvIxG3EOoEpa81gpcKOQwgEAAwIAA3kAAzYE'
    top_id = 'AgACAgIAAxkBAAEULRRoU-MFD7cfnIKEJm2YELu1gi50MAACnvAxGwE_oUpRS_1RGCh28QEAAwIAA3kAAzYE'

    BASE_MSG = """
<b>Assalomu alaykum! PremiumHub botimizga xush kelibsiz!</b>
<i>
Siz ushbu bot orqali qanday imkoniyatlarga ega boʻlishingizni bilasizmi ? Bilmaganlar uchun pastda ko'rsatib o'tamiz 👇

1. Tezda Premium va Stars xarid qilish 🌟

2. Arzon narxlar hamta sifatli xizmatlarimiz orqali Premium va Stars olish 💫

3. Bonuslar olish orqali Telegram Premium hamda Telegram Stars  ni tekinga olish imkoniyati✨ 

Bot qoʻllanmasini oʻqisangiz, nima qilish kerakligini bilib olasiz😊

<b>‼️ Xizmatlarimiz kafolatlangan‼️</b>

Mamnun mijozlarimiz otzivlarini @PremiumHub shu  koʻrishingiz va ishonchni yanayam mustahkamlash uchun guruhimiz aʼzolaridan soʻrashingiz mumkin. 

Siz ham mamnun mijozlarimiz qatorida boʻlishingizni chin yurakdan tilab qolamiz!</i>
    """
    GET_PREMIUM_AND_STARS = """
<b>Sizga haligacha Telegram Premium sovgʻa qilishmadimi?</b>
<i>
➖ Telegram Premium obunani sovgʻa sifatida tekinga olishni istaysizmi?
 
Shunchaki pastdagi havola orqali doʻstlaringizni taklif qiling. Botning oʻzi sizga pul toʻlaydi. Toʻplangan pullarga Premium obunasini follashtirishingiz mumkin.</i>

<b>Hoziroq o'z sovg'angiz sari olg'a bosing:</b> URL
"""


class KeyboardText:
    base = {
        'uz': ["🌟 Bepul Premium va Stars olish 🌟", "💸 Premium narxlari", "⭐ Stars Narxlari", "🏆 TOP Reyting",
               "🎁 Bonus olish", "💳 Mening Hisobim", "📝 Qo'llanma", "👨‍💻 Administrator", "💎 Test ishlab bonus olish 🆕"],
        'ru': ["Личный кабинет", "Отправить отзыв", "Посмотреть статистику", "Настройки ⚙️"],
        'en': ["Personal account", "Send feedback", "View statistics", "Settings ⚙️"],
    }
    admin = {
        'uz': ["💠 Xabar yuborish", "🔍 Foydalanuvchi qidirish"],
        'ru': ["Личный кабинет", "Отправить отзыв", "Посмотреть статистику", "Настройки ⚙️"],
        'en': ["Personal account", "Send feedback", "View statistics", "Settings ⚙️"],
    }
    referral = {
        'uz': "📤 Do'stlarga Ulashish",
    }
    send = {
        "uz": "Yuborish 📤",
        "ru": "Отправить 📤",
        "en": "Send 📤",
    }
    back = {
        'uz': "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back"
    }
    channel = {
        'uz': 'Tekshirish ♻️',
        'ru': 'Проверить ♻️',
        'en': 'Check ♻️', }

    channel_set = {
        'uz': ["Kanal qo'shish", "⬅️ Orqaga"],
        'ru': ["Добавить канал", "⬅️ Назад"],
        'en': ["Add channel", "⬅️ Back"],
    }

    manager = {
        'uz': ["Zakaslar Statistikasi", "Foydalanuvchilar Statistikasi", "Kunlik hisobot olish"],
        'ru': ["Статистика заказов", "Статистика пользователей", "Получить ежедневный отчет"],
    }

    get_location = {
        'uz': ["📍 Mening manzillarim", "🗺 Manzilni tanlash", "⬅️ Orqaga"],
        'ru': ["📍 Мои адреса", "🗺 Выбрать адрес", "⬅️ Назад"],
        'en': ["📍 My addresses", "🗺 Select address", "⬅️ Back"],
    }

    confirmation = {
        'uz': ["Ha ✅", "⬅️ Orqaga"],
        'ru': ["Да ✅", "⬅️ Назад"],
        'en': ["Yes ✅", "⬅️ Back"],
    }

    yes_no = {
        'uz': ["Ha ✅", "Yo'q ❌"],
        'ru': ["Да ✅", "Нет ❌"],
        'en': ["Yes ✅", "No ❌"],
    }

    settings = {
        'uz': ["🇺🇿 Tilni o'zgartirish 🔄", "☎️ Telefon nomerni o'zgartirish 🔄", "⬅️ Orqaga"],
        'ru': ["🇷🇺 Изменить язык 🔄", "☎️ Изменить номер телефона 🔄", "⬅️ Назад"],
        'en': ["🇺🇿 Change language 🔄", "☎️ Change phone number 🔄", "⬅️ Back"],
    }


class MenejerText:
    main = {
        'uz': "<b>Admin panelga xush kelibsiz!!!</b>",
        'ru': "<b>Добро пожаловать в панель администратора!!!</b>",
        'en': "<b>Welcome to the admin panel!!!</b>",
    }

    not_found_finished_order = {
        'uz': "<b>Tugatilgan yoki qaytarilgan buyurtmalar topilmadi</b>",
        'ru': "<b>Завершенные или возвращенные заказы не найдены</b>",
        'en': "<b>Finished or returned orders not found</b>",
    }


class SupplierText:
    main = {
        'uz': "<b>Kuryer panelga xush kelibsiz!!!</b>",
        'ru': "<b>Добро пожаловать в панель курьера!!!</b>",
        'en': "<b>Welcome to the courier panel!!!</b>",
    }

    not_found_finished_order = {
        'uz': "<b>Sizda tugatilgan buyurtmalar topilmadi</b>",
        'ru': "<b>У вас нет завершенных заказов</b>",
        'en': "<b>You don't have finished orders</b>",
    }

    no_order = {
        'uz': "<b>Sizda buyurtma yo'q</b>",
        'ru': "<b>У вас нет заказа</b>",
        'en': "<b>You don't have an order</b>",
    }
    one_order_code = {
        'uz': "<b>Bajarilayotgan buyurtma raqamini kiriting !!!\n\nLakatsiyasi va statuslarini o'zgartirish imkoniyati mavjud bo'ladi</b>",
        'ru': "<b>Введите номер заказа, который выполняется !!!\n\nВы можете изменить его местоположение и статус</b>",
        'en': "<b>Enter the order number that is being executed !!!\n\nYou can change its location and status</b>",
    }

    error_order_id = {
        'uz': "<b>Bunday buyurtma xato kiritidi !!!\n\n Faqat ramalardan iborat bo'lishi kerak!!!</b>",
        'ru': "<b>Такой заказ введен неправильно !!!\n\n Должен состоять только из цифр!!!</b>",
        'en': "<b>Such an order is entered incorrectly !!!\n\n Must consist only of numbers!!!</b>",
    }

    order_status = {
        'uz': "<b>Buyurtma statusini o'zgartirildi</b>",
        'ru': "<b>Статус заказа изменен</b>",
        'en': "<b>Order status changed</b>",
    }

    error_order_status = {
        'uz': "<b>Buyurtma statusini o'zgartirishda xatolik !!!</b>",
        'ru': "<b>Ошибка при изменении статуса заказа !!!</b>",
        'en': "<b>Error changing order status !!!</b>",
    }

    order_completed = {
        'uz': "Buyurtmangiz: {}",
        'ru': "Ваш заказ: {}",
        'en': "Your order: {}",
    }
    order_status_to_admins = {
        'uz': "🛍 Buyurtma holati: \n\nNomeri: №{}\nYetkazib beruvchi: {}\nStatusi: {}",
        'ru': "🛍 Статус заказа: \n\nНомер: №{}\nДоставщик: {}\nСтатус: {}",
        'en': "🛍 Order status: \n\nNumber: №{}\nCourier: {}\nStatus: {}",
    }
