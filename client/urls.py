from django.urls import path
from .views import ClientRegistrationView, ClientLoginView, ClientPasswordChangeView, OrderUpdateView, confirm_order, \
    NotifyWorkersView, JobListByCategoryView, OrderCategoryJobCreateView

urlpatterns = [
    path('register/', ClientRegistrationView.as_view(), name='client-register'),
    path('login/', ClientLoginView.as_view(), name='client-login'),
    path('password-change/', ClientPasswordChangeView.as_view(), name='client-password-change'),

    # order
    path('category-job/', JobListByCategoryView.as_view(), name='category-job'),
    path('category-job/<int:category_id>/', JobListByCategoryView.as_view(), name='category-job'),
    path('order-create-category-job/', OrderCategoryJobCreateView.as_view(), name='create-order'),
    path('update-order/<int:order_id>/', OrderUpdateView.as_view(), name='update-order'),
    path('order-add-workers/', NotifyWorkersView.as_view(), name='order-add-workers'),


]
