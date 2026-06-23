from .utils import DELIVERY_FEE

def site_info(request):
    return {
        'SITE_PHONE': '774014812',
        'SITE_PHONE_TEL': '+967774014812',
        'SITE_WHATSAPP': '967774014812',
        'SITE_LOCATION': 'اليمن - صنعاء',
        'SITE_FULL_ADDRESS': 'مطعم ومطبخ الحرمين - صنعاء، اليمن',
        'SITE_MAP_URL': 'https://maps.app.goo.gl/VrxDhnYsH2WFUjZU8',
        'SITE_MAP_EMBED': 'https://www.google.com/maps?q=%D9%85%D8%B7%D8%B9%D9%85+%D9%88%D9%85%D8%B7%D8%A8%D8%AE+%D8%A7%D9%84%D8%AD%D8%B1%D9%85%D9%8A%D9%86+%D8%B5%D9%86%D8%B9%D8%A7%D8%A1+%D8%A7%D9%84%D9%8A%D9%85%D9%86&hl=ar&z=16&output=embed',
        'SITE_HOURS': 'متاح للطلب في أي وقت',
        'SITE_EMAIL': 'info@alharmain.com',
        'DELIVERY_FEE': DELIVERY_FEE,
    }
