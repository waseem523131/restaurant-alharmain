from datetime import time
from decimal import Decimal

from django.utils import timezone

OPEN_TIME = time(6, 0)
CLOSE_TIME = time(15, 0)
DELIVERY_FEE = Decimal('15.00')
CLOSED_MESSAGE = (
    'نعتذر، المطعم مغلق حالياً. ساعات العمل اليومية من 6:00 صباحاً حتى 3:00 عصراً. '
    'يرجى العودة خلال أوقات الدوام لتقديم طلبك.'
)


def is_restaurant_open():
    now = timezone.localtime().time()
    return OPEN_TIME <= now < CLOSE_TIME
