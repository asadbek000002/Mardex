from django.urls import path
from .views import WorkerRegistrationView, WorkerLoginView, WorkerPasswordChangeView, websocket_test

urlpatterns = [
    path('register/', WorkerRegistrationView.as_view(), name='worker-register'),
    path('login/', WorkerLoginView.as_view(), name='worker-login'),
    path('password-change/', WorkerPasswordChangeView.as_view(), name='worker-password-change'),

    path('websocket/', websocket_test, name='websocket_test'),
]
