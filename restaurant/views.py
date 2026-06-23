import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm, ContactForm, DeliveryOrderForm, ReviewForm
from .models import Category, DeliveryOrder, Dish, PaymentAccount, Testimonial
from .utils import DELIVERY_FEE

PENDING_ORDER_SESSION_KEY = 'pending_order'


def _get_pending_order(request):
    return request.session.get(PENDING_ORDER_SESSION_KEY)


def _set_pending_order(request, data):
    request.session[PENDING_ORDER_SESSION_KEY] = data
    request.session.modified = True


def _clear_pending_order(request):
    if PENDING_ORDER_SESSION_KEY in request.session:
        del request.session[PENDING_ORDER_SESSION_KEY]
        request.session.modified = True


def index(request):
    featured_dishes = Dish.objects.filter(is_featured=True, is_available=True, is_deleted=False)[:4]
    if featured_dishes.count() < 4:
        featured_dishes = Dish.objects.filter(is_available=True, is_deleted=False)[:4]

    context = {
        'featured_dishes': featured_dishes,
    }
    return render(request, 'restaurant/index.html', context)


def about(request):
    return render(request, 'restaurant/about.html')


def ratings(request):
    reviews = Testimonial.objects.filter(is_active=True, is_deleted=False)
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
    dishes = Dish.objects.filter(is_available=True, is_deleted=False).select_related('category')
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
        dish = get_object_or_404(Dish, pk=dish_id, is_available=True, is_deleted=False)

    form = DeliveryOrderForm()

    if request.method == 'POST':
        if not dish:
            messages.error(request, 'يرجى اختيار صنف من القائمة أولاً.')
        else:
            form = DeliveryOrderForm(request.POST)
            if form.is_valid():
                quantity = form.cleaned_data['quantity']
                unit_price = dish.price
                total_amount = (unit_price * quantity) + DELIVERY_FEE

                _set_pending_order(request, {
                    'dish_id': dish.pk,
                    'name': form.cleaned_data['name'],
                    'phone': form.cleaned_data['phone'],
                    'address': form.cleaned_data['address'],
                    'quantity': quantity,
                    'notes': form.cleaned_data.get('notes', ''),
                    'item_name': dish.name,
                    'unit_price': str(unit_price),
                    'delivery_fee': str(DELIVERY_FEE),
                    'total_amount': str(total_amount),
                })
                return redirect('restaurant:checkout')
            messages.error(request, 'يرجى تصحيح الأخطاء في نموذج الطلب.')

    context = {
        'form': form,
        'dish': dish,
        'dishes': Dish.objects.filter(is_available=True, is_deleted=False),
        'delivery_fee': DELIVERY_FEE,
        'unit_price': dish.price if dish else 0,
        'initial_total': (dish.price + DELIVERY_FEE) if dish else DELIVERY_FEE,
    }
    return render(request, 'restaurant/delivery.html', context)


def checkout(request):
    pending = _get_pending_order(request)
    if not pending:
        messages.warning(request, 'لا يوجد طلب قيد الإتمام. يرجى تعبئة بيانات التوصيل أولاً.')
        return redirect('restaurant:delivery')

    dish = get_object_or_404(Dish, pk=pending['dish_id'], is_available=True, is_deleted=False)
    form = CheckoutForm()

    payment_accounts = {
        account.method: account
        for account in PaymentAccount.objects.filter(is_active=True)
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = DeliveryOrder(
                name=pending['name'],
                phone=pending['phone'],
                address=pending['address'],
                dish=dish,
                item_name=pending['item_name'],
                quantity=pending['quantity'],
                notes=pending.get('notes', ''),
                unit_price=pending['unit_price'],
                delivery_fee=pending['delivery_fee'],
                total_amount=pending['total_amount'],
                payment_method=form.cleaned_data['payment_method'],
                transaction_id=form.cleaned_data.get('transaction_id', ''),
                order_status=DeliveryOrder.OrderStatus.PENDING_REVIEW,
                payment_status=DeliveryOrder.PaymentStatus.UNCONFIRMED,
            )
            order.save()
            _clear_pending_order(request)
            return redirect('restaurant:order_success', order_id=order.pk)

    context = {
        'form': form,
        'pending': pending,
        'dish': dish,
        'payment_accounts': payment_accounts,
        'electronic_methods_json': json.dumps(list(DeliveryOrder.ELECTRONIC_METHODS)),
    }
    return render(request, 'restaurant/checkout.html', context)


def order_success(request, order_id):
    order = get_object_or_404(DeliveryOrder, pk=order_id)
    context = {
        'order': order,
    }
    return render(request, 'restaurant/order_success.html', context)


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
