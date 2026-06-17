from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ContactForm, DeliveryOrderForm, ReviewForm
from .models import Category, Dish, Testimonial
from .utils import CLOSED_MESSAGE, DELIVERY_FEE, is_restaurant_open


def index(request):
    featured_dishes = Dish.objects.filter(is_featured=True, is_available=True)[:4]
    if featured_dishes.count() < 4:
        featured_dishes = Dish.objects.filter(is_available=True)[:4]

    context = {
        'featured_dishes': featured_dishes,
    }
    return render(request, 'restaurant/index.html', context)


def about(request):
    return render(request, 'restaurant/about.html')


def ratings(request):
    reviews = Testimonial.objects.filter(is_active=True)
    review_form = ReviewForm()

    if request.method == 'POST':
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review_form.save()
            messages.success(request, 'شكراً لك! تم إرسال تقييمك بنجاح.')
            return redirect('restaurant:ratings')
        messages.error(request, 'يرجى تعبئة جميع الحقول المطلوبة.')

    average = Testimonial.get_average_rating()
    selected_rating = request.POST.get('rating') if request.method == 'POST' else None

    context = {
        'reviews': reviews,
        'review_form': review_form,
        'average_rating': average,
        'average_stars': round(average) if average else 0,
        'reviews_count': Testimonial.get_reviews_count(),
        'selected_rating': selected_rating,
    }
    return render(request, 'restaurant/ratings.html', context)


def menu(request):
    dishes = Dish.objects.filter(is_available=True).select_related('category')
    categories = Category.objects.all()

    paginator = Paginator(dishes, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'dishes': page_obj,
    }
    return render(request, 'restaurant/menu.html', context)


def delivery(request):
    dish = None
    dish_id = request.GET.get('dish') or request.POST.get('dish')

    if dish_id:
        dish = get_object_or_404(Dish, pk=dish_id, is_available=True)

    is_open = is_restaurant_open()
    form = DeliveryOrderForm()

    if request.method == 'POST':
        if not is_open:
            messages.error(request, CLOSED_MESSAGE)
        elif not dish:
            messages.error(request, 'يرجى اختيار صنف من القائمة أولاً.')
        else:
            form = DeliveryOrderForm(request.POST)
            if form.is_valid():
                order = form.save(commit=False)
                order.dish = dish
                order.item_name = dish.name
                order.unit_price = dish.price
                order.delivery_fee = DELIVERY_FEE
                order.total_amount = (dish.price * order.quantity) + DELIVERY_FEE
                order.save()
                messages.success(
                    request,
                    'تم تأكيد طلبك بنجاح! سنتواصل معك قريباً لإتمام التوصيل.',
                )
                return redirect(f'{reverse("restaurant:delivery")}?dish={dish.pk}')
            messages.error(request, 'يرجى تصحيح الأخطاء في نموذج الطلب.')

    context = {
        'form': form,
        'dish': dish,
        'dishes': Dish.objects.filter(is_available=True),
        'is_open': is_open,
        'delivery_fee': DELIVERY_FEE,
        'closed_message': CLOSED_MESSAGE,
        'unit_price': dish.price if dish else 0,
        'initial_total': (dish.price + DELIVERY_FEE) if dish else DELIVERY_FEE,
    }
    return render(request, 'restaurant/delivery.html', context)


def contact(request):
    contact_form = ContactForm()

    if request.method == 'POST':
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, 'تم إرسال رسالتك بنجاح! شكراً لتواصلك معنا.')
            return redirect('restaurant:contact')
        messages.error(request, 'يرجى تصحيح الأخطاء في نموذج التواصل.')

    context = {
        'contact_form': contact_form,
    }
    return render(request, 'restaurant/contact.html', context)
