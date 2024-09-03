from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order
from job.models import CategoryJob, Job

User = get_user_model()


class ClientRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'password', 'password_confirmation', 'region', 'city']

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        # Parol tasdiqlash maydonini o'chirish
        validated_data.pop('password_confirmation')

        client = User(
            phone=validated_data['phone'],
            full_name=validated_data['full_name'],
            region=validated_data.get('region'),
            city=validated_data.get('city'),
            role="client"
        )
        client.set_password(validated_data['password'])
        client.save()
        return client


class ClientLoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone = data.get("phone")
        password = data.get("password")
        client = User.objects.filter(phone=phone).first()

        if client and client.check_password(password):
            return client
        else:
            raise serializers.ValidationError("Invalid phone or password")


class ClientPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError("New passwords do not match.")
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class OrderCategoryJobSerializers(serializers.ModelSerializer):
    job_id = serializers.ListField(child=serializers.IntegerField(), write_only=True)
    job_category = serializers.PrimaryKeyRelatedField(queryset=CategoryJob.objects.all(), write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'job_category', 'job_id']

    def create(self, validated_data):
        job_category = validated_data.get('job_category')
        job_id = validated_data.get('job_id')

        order = Order.objects.create(job_category=job_category)

        jobs = Job.objects.filter(id__in=job_id, category_job=job_category)
        order.job_id.set(jobs)

        return order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'desc', 'price', 'full_desc', 'city', 'region', 'gender', 'work_count', 'images']


class NotifySerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    worker_ids = serializers.ListField(child=serializers.IntegerField())
    message = serializers.DictField()


class CategoryJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryJob
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"

