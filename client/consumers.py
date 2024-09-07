# client/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from users.models import AbstractUser
from django.conf import settings


class BaseConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', None)
        self.user_channel_name = self.channel_name

        # Agar foydalanuvchi mavjud bo'lmasa, ulanishni rad etish
        if not self.user or not hasattr(self.user, 'phone'):
            await self.close()
            return

        try:
            # `AbstractUser` modelidan foydalanuvchini olish
            self.user_instance = await database_sync_to_async(AbstractUser.objects.get)(phone=self.user.phone)

            # Foydalanuvchi online holatini yangilash
            await self.set_user_online_status(True)

            # Foydalanuvchi ID asosida guruhga qo'shish
            group_name = f"user_{self.user_instance.id}"
            await self.channel_layer.group_add(
                group_name,
                self.channel_name
            )

            await self.accept()
        except AbstractUser.DoesNotExist:
            # Agar foydalanuvchi topilmasa, ulanishni yopish
            await self.close()

    async def disconnect(self, close_code):
        # Foydalanuvchini offline deb belgilash
        await self.set_user_online_status(False)

        # Har bir guruhdan chiqarish
        group_name = f"user_{self.user_instance.id}"
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )

    async def send_message(self, message_type, message_data):
        await self.send(text_data=json.dumps({
            'type': message_type,
            **message_data
        }))

    @database_sync_to_async
    def set_user_online_status(self, status):
        """Foydalanuvchi online holatini belgilash"""
        self.user_instance.is_online = status
        self.user_instance.save()


class OrderNotificationConsumer(BaseConsumer):
    async def connect(self):
        # Ota klassning connect metodini chaqirish
        await super().connect()

        # Order guruhini qo'shish
        self.order_groups = []

    async def disconnect(self, close_code):
        # Ota klassning disconnect metodini chaqirish
        await super().disconnect(close_code)

        # Har bir guruhdan chiqarish
        for group_name in self.order_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    async def order_message_worker(self, event):
        order_id = event.get('order_id')
        message = event.get('message')
        print(message)
        confirm_url = f"{settings.SITE_URL}/confirm_order/{order_id}/"

        # Foydalanuvchiga order haqida xabar yuborish
        await self.send_message('order_message_worker', {
            'message': message,
            'confirm_url': confirm_url,
            'order_id': order_id
        })


class ClientNotificationConsumer(BaseConsumer):
    async def connect(self):
        # Ota klassning connect metodini chaqirish
        await super().connect()

        # Order guruhini qo'shish
        self.order_groups = []
        print('clinet', self.order_groups)

    async def disconnect(self, close_code):
        # Ota klassning disconnect metodini chaqirish
        await super().disconnect(close_code)

        # Har bir guruhdan chiqarish
        for group_name in self.order_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    async def order_message_client(self, event):
        order_id = event.get('order_id')
        worker_id = event.get('worker_id')
        ful_name = event.get('ful_name')
        phone = event.get('phone')
        view_count = event.get('view_count')



        # Foydalanuvchiga order haqida xabar yuborish
        await self.send_message('order_message_client', {
            'order_id': order_id,
            "worker_id": worker_id,
            'ful_name': ful_name,
            'phone': phone,
            'view_count': view_count
        })
