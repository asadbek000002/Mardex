from django.urls import path
from .views import ClientRegistrationView, ClientLoginView, ClientPasswordChangeView, OrderCreateView, confirm_order

urlpatterns = [
    path('register/', ClientRegistrationView.as_view(), name='client-register'),
    path('login/', ClientLoginView.as_view(), name='client-login'),
    path('password-change/', ClientPasswordChangeView.as_view(), name='client-password-change'),

    # order
    path('create-order/', OrderCreateView.as_view(), name='create-order'),
    # path('confirm_order/<int:order_id>/', confirm_order, name='confirm_order'),

]
