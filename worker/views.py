from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import WorkerRegistrationSerializer, WorkerLoginSerializer, \
    WorkerPasswordChangeSerializer

from users.models import AbstractUser


def websocket_test(request):
    return render(request, 'web.html')


class WorkerRegistrationView(generics.CreateAPIView):
    queryset = AbstractUser.objects.all()
    serializer_class = WorkerRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worker = serializer.save()

        refresh = RefreshToken.for_user(worker)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class WorkerLoginView(generics.GenericAPIView):
    serializer_class = WorkerLoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        worker = serializer.validated_data

        refresh = RefreshToken.for_user(worker)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "worker": WorkerRegistrationSerializer(worker).data,
        }, status=status.HTTP_200_OK)


class WorkerPasswordChangeView(generics.GenericAPIView):
    serializer_class = WorkerPasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Password updated successfully."})

    def perform_update(self, serializer):
        serializer.save()
