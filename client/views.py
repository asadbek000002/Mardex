from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import ClientRegistrationSerializer, ClientLoginSerializer, ClientPasswordChangeSerializer, \
    OrderSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Order

from users.models import AbstractUser


class ClientRegistrationView(generics.CreateAPIView):
    queryset = AbstractUser.objects.all()
    serializer_class = ClientRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()

        refresh = RefreshToken.for_user(client)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class ClientLoginView(generics.GenericAPIView):
    serializer_class = ClientLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worker = serializer.validated_data

        refresh = RefreshToken.for_user(worker)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class ClientPasswordChangeView(generics.GenericAPIView):
    serializer_class = ClientPasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Password updated successfully."})

    def perform_update(self, serializer):
        serializer.save()


class OrderCreateView(generics.GenericAPIView):
    serializer_class = OrderSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()  # Bu yerda yangi order yaratildi
            order = serializer.save()  # Bu yerda yangi order yaratildi

            order_id= order.id
            category_id = order.job_category.id
            job_ids = [job.id for job in order.job_id.all()]  # Orderning barcha job'lari olinadi
            image_url = order.images.url if order.images else None
            message = {
                "text": f"Yangi buyurtma: {order.price} | {order.desc}",
                "image_url": image_url  # Tasvir URL manzili xabarga kiritilgan
            }

            create_order_and_notify(category_id=category_id, job_ids=job_ids, message=message, order_id=order_id)  # Xabar yuborish

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





def create_order_and_notify(category_id, job_ids, message, order_id):
    channel_layer = get_channel_layer()

    for job_id in job_ids:
        group_name = f"category_{category_id}_job_{job_id}"
        # Sinxron kodni asinxron kontekstda chaqirish
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "order_message",
                "message": message,
                "order_id": order_id
            }
        )

        print(f"group {group_name}")


def confirm_order(request, order_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponse("User not authenticated", status=401)

    order = get_object_or_404(Order, id=order_id)

    # Workerni orderning accepted_workers maydoniga qo'shish
    if user not in order.accepted_workers.all():
        order.accepted_workers.add(user)
        order.save()

    return HttpResponse("Order confirmed", status=200)