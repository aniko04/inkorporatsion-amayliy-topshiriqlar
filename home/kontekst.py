"""Har bir shablonga qo'shiladigan umumiy qiymatlar (context processor)."""


def sayt_manzili(request):
    """Meta teglar uchun saytning to'liq manzili, masalan `https://texnoedu.uz`.

    NEGA `request.scheme` NING O'ZI YETARLI EMAS: sayt nginx orqasida turadi va
    TLS o'sha yerda tugaydi — Django'ga so'rov oddiy HTTP bo'lib keladi. Django
    ulanish himoyalanganini faqat `SECURE_PROXY_SSL_HEADER` o'rnatilgan bo'lsa
    biladi, u esa `DJANGO_HTTPS=1` bo'lgandagina o'rnatiladi. Serverda `.env`
    yozilmagan bo'lsa, `request.scheme` "http" qaytaradi va `og:url`,
    `og:image`, `canonical` — hammasi noto'g'ri `http://` bo'lib chiqadi.

    Buning oqibati ko'rinmas, lekin real: Telegram va boshqa xizmatlar HTTPS
    sahifadagi HTTP rasmni yuklamasligi mumkin, qidiruv tizimlari esa `http://`
    va `https://` ni ikki xil sahifa deb hisoblaydi.

    Shuning uchun manzil shu yerda aniqlanadi va `.env` ga bog'liq emas:
    mahalliy kompyuterda `http`, haqiqiy domenda har doim `https`.
    """
    host = request.get_host()
    mahalliy = host.split(':')[0] in ('localhost', '127.0.0.1', '0.0.0.0', 'testserver')
    sxema = request.scheme if mahalliy else 'https'
    return {'sayt_asos': f'{sxema}://{host}'}
