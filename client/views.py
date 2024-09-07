from django.contrib.auth.decorators import login_not_required
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from job.models import CategoryJob, Job
from .serializers import ClientRegistrationSerializer, ClientLoginSerializer, ClientPasswordChangeSerializer, \
    OrderSerializer, NotifySerializer, CategoryJobSerializer, JobSerializer, OrderCategoryJobSerializers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import Order

from django.contrib.auth import get_user_model

User = get_user_model()


class ClientRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
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


class JobListByCategoryView(APIView):
    def get(self, request, category_id=None):
        # Barcha kategoriyalarni olish
        categories = CategoryJob.objects.all()
        category_serializer = CategoryJobSerializer(categories, many=True)

        if category_id:
            jobs = Job.objects.filter(category_job_id=category_id)
            job_serializer = JobSerializer(jobs, many=True)

            # Response ichida kategoriyalar va ishlar ro'yxatini qaytarish
            return Response({
                'job_category': category_serializer.data,
                'job_ids': job_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            # Agar category_id berilmagan bo'lsa, faqat kategoriyalarni qaytarish
            return Response({
                'job_category': category_serializer.data
            }, status=status.HTTP_200_OK)


class OrderCategoryJobCreateView(generics.GenericAPIView):
    serializer_class = OrderCategoryJobSerializers

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save()
            return Response({'order_id': order.id, 'message': 'Order created successfully.'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderUpdateView(generics.GenericAPIView):
    serializer_class = OrderSerializer

    def put(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()

            # Yangi buyurtma haqida xabar yaratish
            message = {
                "text": f"Yangi buyurtma: {order.desc} | price: {order.price}",
            }
            temp_worker_list = self.filter_workers({
                'city': request.data.get('city'),
                'gender': request.data.get('gender'),
                'job_category': order.job_category,
                'job_id': order.job_id.all().values_list('id', flat=True),
            })

            # Foydalanuvchiga javob berish
            return Response({
                'order_id': order.id,
                'workers': [
                    {
                        'id': worker.id,
                        'avatar': worker.avatar.url if worker.avatar else None,
                        'full_name': worker.full_name
                    }
                    for worker in temp_worker_list],
                'message': message
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def filter_workers(self, data):
        city = data.get('city')
        job_ids = data.get('job_id', [])  # job_ids ro'yxat sifatida olinadi
        job_category = data.get('job_category')
        gender = data.get('gender')

        worker_ids = set()

        temp_worker_list = []

        query = Q()

        if city:
            query &= Q(city=city)
        if job_category:
            query &= Q(job_category=job_category)
        if job_ids:
            query &= Q(job_id__in=job_ids)
        if gender:
            query &= Q(gender=gender)


        workers = User.objects.filter(query)

        temp_worker_list = []

        for worker in workers:
            if worker.id not in worker_ids:
                worker_ids.add(worker.id)
                temp_worker_list.append(worker)

        return temp_worker_list


class NotifyWorkersView(generics.GenericAPIView):
    serializer_class = NotifySerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            worker_ids = serializer.validated_data['worker_ids']
            message = serializer.validated_data['message']

            # Tanlangan ishchilarni olish
            workers = User.objects.filter(id__in=worker_ids)

            # Xabar yuborish
            self.create_order_notify_for_worker(workers, message, order_id)

            return Response({'status': 'Notifications sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create_order_notify_for_worker(self, worker_list, message, order_id):
        channel_layer = get_channel_layer()
        for worker in worker_list:
            user_channel_name = f"user_{worker.id}"
            async_to_sync(channel_layer.group_send)(
                user_channel_name,
                {
                    "type": "order_message_worker",
                    "message": message,
                    "order_id": order_id
                }
            )


@api_view(['POST'])
def accepted_workers_notify_for_client(request, order_id):
    user = request.user
    if not user.is_authenticated:
        return HttpResponse("User not authenticated", status=401)

    order = get_object_or_404(Order, id=order_id)

    # Workerni orderning accepted_workers maydoniga qo'shish
    if user not in order.accepted_workers.all():
        order.accepted_workers.add(user)
        order.view_count += 1
        order.save()

        channel_layer = get_channel_layer()
        # Orderni yaratgan userga xabar yuborish
        client = order.client  # Orderni yaratgan user

        user_channel_name = f"user_{client.id}"
        async_to_sync(channel_layer.group_send)(
            user_channel_name,
            {
                "type": "order_message_client",
                "worker_id": user.id,
                "ful_name": user.full_name,
                "phone": user.phone,
                "order_id": order_id,
                "view_count": order.view_count

            }
        )

    return HttpResponse("Order confirmed", status=200)
