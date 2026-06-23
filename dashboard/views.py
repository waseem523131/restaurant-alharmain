import json
from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from restaurant.models import (
    Category,
    ContactMessage,
    DeliveryOrder,
    Dish,
    PaymentAccount,
    Reservation,
    Testimonial,
)

from .decorators import staff_required, staff_required_ajax
from .forms import (
    CategoryForm,
    DeliveryOrderUpdateForm,
    DishForm,
    OrderFilterForm,
    PaymentAccountForm,
    ReservationUpdateForm,
    TestimonialForm,
)
from .mixins import StaffRequiredMixin


def soft_delete(instance):
    instance.is_deleted = True
    instance.deleted_at = timezone.now()
    instance.save(update_fields=['is_deleted', 'deleted_at'])


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user and user.is_staff:
            login(request, user)
            return redirect(request.GET.get('next') or 'dashboard:home')
        messages.error(request, 'بيانات الدخول غير صحيحة أو ليس لديك صلاحية.')

    return render(request, 'dashboard/login.html')


@login_required(login_url='dashboard:login')
def logout_view(request):
    logout(request)
    return redirect('dashboard:login')


@staff_required
def home(request):
    today = timezone.localdate()
    week_ago = today - timedelta(days=6)
    active_orders = DeliveryOrder.objects.filter(is_deleted=False)

    stats = {
        'orders_today': active_orders.filter(created_at__date=today).count(),
        'pending_orders': active_orders.filter(
            order_status=DeliveryOrder.OrderStatus.PENDING_REVIEW,
        ).count(),
        'revenue_today': active_orders.filter(
            created_at__date=today,
            order_status=DeliveryOrder.OrderStatus.DELIVERED,
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
        'dishes_count': Dish.objects.filter(is_deleted=False, is_available=True).count(),
        'reviews_count': Testimonial.objects.filter(is_deleted=False, is_active=True).count(),
        'avg_rating': Testimonial.get_average_rating(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
    }

    daily_orders = (
        active_orders.filter(created_at__date__gte=week_ago)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )
    daily_revenue = (
        active_orders.filter(
            created_at__date__gte=week_ago,
            order_status=DeliveryOrder.OrderStatus.DELIVERED,
        )
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Sum('total_amount'))
        .order_by('day')
    )
    status_breakdown = list(
        active_orders.values('order_status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    chart_labels = [(week_ago + timedelta(days=i)).strftime('%d/%m') for i in range(7)]
    orders_map = {item['day']: item['count'] for item in daily_orders}
    revenue_map = {item['day']: float(item['total'] or 0) for item in daily_revenue}

    chart_data = {
        'labels': chart_labels,
        'orders': [
            orders_map.get(week_ago + timedelta(days=i), 0) for i in range(7)
        ],
        'revenue': [
            revenue_map.get(week_ago + timedelta(days=i), 0) for i in range(7)
        ],
        'status_labels': [
            dict(DeliveryOrder.OrderStatus.choices).get(item['order_status'], item['order_status'])
            for item in status_breakdown
        ],
        'status_counts': [item['count'] for item in status_breakdown],
    }

    context = {
        'stats': stats,
        'recent_orders': active_orders.select_related('dish')[:8],
        'chart_data_json': json.dumps(chart_data, ensure_ascii=False),
    }
    return render(request, 'dashboard/home.html', context)


class OrderListView(StaffRequiredMixin, ListView):
    model = DeliveryOrder
    template_name = 'dashboard/orders/list.html'
    context_object_name = 'orders'
    paginate_by = 15

    def get_queryset(self):
        qs = DeliveryOrder.objects.filter(is_deleted=False).select_related('dish')
        self.filter_form = OrderFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            q = self.filter_form.cleaned_data.get('q')
            order_status = self.filter_form.cleaned_data.get('order_status')
            payment_status = self.filter_form.cleaned_data.get('payment_status')
            if q:
                qs = qs.filter(
                    Q(name__icontains=q)
                    | Q(phone__icontains=q)
                    | Q(item_name__icontains=q)
                    | Q(transaction_id__icontains=q)
                )
            if order_status:
                qs = qs.filter(order_status=order_status)
            if payment_status:
                qs = qs.filter(payment_status=payment_status)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = getattr(self, 'filter_form', OrderFilterForm())
        context['order_status_choices'] = DeliveryOrder.OrderStatus.choices
        context['payment_status_choices'] = DeliveryOrder.PaymentStatus.choices
        return context


class OrderDetailView(StaffRequiredMixin, DetailView):
    model = DeliveryOrder
    template_name = 'dashboard/orders/detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return DeliveryOrder.objects.filter(is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = DeliveryOrderUpdateForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = DeliveryOrderUpdateForm(request.POST, instance=self.object)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الطلب بنجاح.')
            return redirect('dashboard:order_detail', pk=self.object.pk)
        context = self.get_context_data(form=form)
        return render(request, self.template_name, context)


@staff_required_ajax
@require_POST
def ajax_update_order(request, pk):
    order = get_object_or_404(DeliveryOrder, pk=pk, is_deleted=False)
    field = request.POST.get('field')
    value = request.POST.get('value')

    allowed = {
        'order_status': dict(DeliveryOrder.OrderStatus.choices),
        'payment_status': dict(DeliveryOrder.PaymentStatus.choices),
    }
    if field not in allowed or value not in allowed[field]:
        return JsonResponse({'success': False, 'error': 'قيمة غير صالحة'}, status=400)

    setattr(order, field, value)
    order.save(update_fields=[field])
    return JsonResponse({
        'success': True,
        'label': allowed[field][value],
    })


@staff_required
@require_POST
def order_delete(request, pk):
    order = get_object_or_404(DeliveryOrder, pk=pk, is_deleted=False)
    soft_delete(order)
    messages.success(request, 'تم حذف الطلب.')
    return redirect('dashboard:orders')


class DishListView(StaffRequiredMixin, ListView):
    model = Dish
    template_name = 'dashboard/dishes/list.html'
    context_object_name = 'dishes'
    paginate_by = 12

    def get_queryset(self):
        qs = Dish.objects.filter(is_deleted=False).select_related('category')
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '')
        if q:
            qs = qs.filter(name__icontains=q)
        if category:
            qs = qs.filter(category_id=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_q'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context


class DishCreateView(StaffRequiredMixin, CreateView):
    model = Dish
    form_class = DishForm
    template_name = 'dashboard/dishes/form.html'
    success_url = reverse_lazy('dashboard:dishes')


class DishUpdateView(StaffRequiredMixin, UpdateView):
    model = Dish
    form_class = DishForm
    template_name = 'dashboard/dishes/form.html'
    success_url = reverse_lazy('dashboard:dishes')

    def get_queryset(self):
        return Dish.objects.filter(is_deleted=False)


@staff_required_ajax
@require_POST
def ajax_toggle_dish(request, pk):
    dish = get_object_or_404(Dish, pk=pk, is_deleted=False)
    field = request.POST.get('field')
    if field not in ('is_available', 'is_featured'):
        return JsonResponse({'success': False, 'error': 'حقل غير مسموح'}, status=400)
    current = getattr(dish, field)
    setattr(dish, field, not current)
    dish.save(update_fields=[field])
    return JsonResponse({'success': True, 'value': getattr(dish, field)})


@staff_required
@require_POST
def dish_delete(request, pk):
    dish = get_object_or_404(Dish, pk=pk, is_deleted=False)
    soft_delete(dish)
    messages.success(request, 'تم حذف الطبق.')
    return redirect('dashboard:dishes')


class CategoryListView(StaffRequiredMixin, ListView):
    model = Category
    template_name = 'dashboard/categories/list.html'
    context_object_name = 'categories'
    paginate_by = 15


class CategoryCreateView(StaffRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/categories/form.html'
    success_url = reverse_lazy('dashboard:categories')


class CategoryUpdateView(StaffRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'dashboard/categories/form.html'
    success_url = reverse_lazy('dashboard:categories')


class ReviewListView(StaffRequiredMixin, ListView):
    model = Testimonial
    template_name = 'dashboard/reviews/list.html'
    context_object_name = 'reviews'
    paginate_by = 12

    def get_queryset(self):
        return Testimonial.objects.filter(is_deleted=False)


class ReviewUpdateView(StaffRequiredMixin, UpdateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'dashboard/reviews/form.html'
    success_url = reverse_lazy('dashboard:reviews')

    def get_queryset(self):
        return Testimonial.objects.filter(is_deleted=False)


@staff_required_ajax
@require_POST
def ajax_toggle_review(request, pk):
    review = get_object_or_404(Testimonial, pk=pk, is_deleted=False)
    review.is_active = not review.is_active
    review.save(update_fields=['is_active'])
    return JsonResponse({'success': True, 'value': review.is_active})


@staff_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Testimonial, pk=pk, is_deleted=False)
    soft_delete(review)
    messages.success(request, 'تم حذف التقييم.')
    return redirect('dashboard:reviews')


class MessageListView(StaffRequiredMixin, ListView):
    model = ContactMessage
    template_name = 'dashboard/messages/list.html'
    context_object_name = 'messages_list'
    paginate_by = 15

    def get_queryset(self):
        qs = ContactMessage.objects.all()
        status = self.request.GET.get('status', '')
        if status == 'unread':
            qs = qs.filter(is_read=False)
        elif status == 'read':
            qs = qs.filter(is_read=True)
        return qs


class MessageDetailView(StaffRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'dashboard/messages/detail.html'
    context_object_name = 'message_obj'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not self.object.is_read:
            self.object.is_read = True
            self.object.save(update_fields=['is_read'])
        return response


@staff_required_ajax
@require_POST
def ajax_toggle_message_read(request, pk):
    message = get_object_or_404(ContactMessage, pk=pk)
    message.is_read = not message.is_read
    message.save(update_fields=['is_read'])
    return JsonResponse({'success': True, 'value': message.is_read})


class ReservationListView(StaffRequiredMixin, ListView):
    model = Reservation
    template_name = 'dashboard/reservations/list.html'
    context_object_name = 'reservations'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation_status_choices'] = Reservation.Status.choices
        return context


@staff_required_ajax
@require_POST
def ajax_update_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    status = request.POST.get('status')
    if status not in dict(Reservation.Status.choices):
        return JsonResponse({'success': False, 'error': 'حالة غير صالحة'}, status=400)
    reservation.status = status
    reservation.save(update_fields=['status'])
    return JsonResponse({
        'success': True,
        'label': reservation.get_status_display(),
    })


class PaymentAccountListView(StaffRequiredMixin, ListView):
    model = PaymentAccount
    template_name = 'dashboard/payments/list.html'
    context_object_name = 'accounts'
    paginate_by = 10


class PaymentAccountCreateView(StaffRequiredMixin, CreateView):
    model = PaymentAccount
    form_class = PaymentAccountForm
    template_name = 'dashboard/payments/form.html'
    success_url = reverse_lazy('dashboard:payments')


class PaymentAccountUpdateView(StaffRequiredMixin, UpdateView):
    model = PaymentAccount
    form_class = PaymentAccountForm
    template_name = 'dashboard/payments/form.html'
    success_url = reverse_lazy('dashboard:payments')
