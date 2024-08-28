from channels.generic.websocket import AsyncWebsocketConsumer
import json
from users.models import AbstractUser
from channels.db import database_sync_to_async
from django.conf import settings
from urllib.parse import urlencode
class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user', None)
        self.worker_groups = []
        self.user_channel_name = self.channel_name

        # Agar foydalanuvchi mavjud bo'lmasa, ulanishni rad etish
        if not self.user or not hasattr(self.user, 'phone'):
            await self.close()
            return

        try:
            # `Worker` modelidan foydalanuvchini olish
            worker = await database_sync_to_async(AbstractUser.objects.get)(phone=self.user.phone)

            # `job_id` va `job_category` ma'lumotlarini olish
            job_ids = await database_sync_to_async(lambda: list(worker.job_id.all()))()
            category_id = await database_sync_to_async(lambda: worker.job_category.id if worker.job_category else None)()

            # Tanlangan `category` va `job_id` mos keladigan guruhlarni yaratish va ulanish
            if category_id:
                for job in job_ids:
                    group_name = f"category_{category_id}_job_{job.id}"
                    self.worker_groups.append(group_name)
                    # Har bir guruhga qo'shish
                    await self.channel_layer.group_add(
                        group_name,
                        self.channel_name
                    )
                print(f"Guruhlar yaratildi: {self.worker_groups}, Foydalanuvchi: {self.user}")

            await self.accept()
        except AbstractUser.DoesNotExist:
            # Agar `worker` topilmasa, ulanishni yopish
            await self.close()

    async def disconnect(self, close_code):
        # Har bir guruhdan chiqarish
        for group_name in self.worker_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    async def order_message(self, event):
        order_id = event.get('order_id')
        confirm_url = f"{settings.SITE_URL}/confirm_order/{order_id}/"
        messages = {
            "text": f"{confirm_url}",
        }

        message = event['message']

        # Yangi order uchun xabar yuborilishi kerak
        if not hasattr(self, 'handled_orders'):
            self.handled_orders = set()  # Xabar yuborilgan orderlar ro'yxati

        # Agar order allaqachon yuborilgan bo'lsa, xabar yubormaslik
        if order_id in self.handled_orders:
            return

        # Har bir guruh uchun xabar yuborish
        for group_name in self.worker_groups:
            # Faqat `user`ni o'z kanaliga yubormaslik
            await self.channel_layer.group_send(
                group_name,
                {
                    "type": "order_message",
                    "message": message,
                    "order_id": order_id
                }
            )

        await self.send(text_data=json.dumps({
            'message': message,
            'messages': messages
        }))

        # Xabar yuborilgan orderlarni saqlash
        self.handled_orders.add(order_id)
