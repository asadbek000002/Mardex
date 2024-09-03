# client/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from users.models import AbstractUser
from django.conf import settings

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
            # `AbstractUser` modelidan foydalanuvchini olish
            self.worker = await database_sync_to_async(AbstractUser.objects.get)(phone=self.user.phone)

            # Foydalanuvchi online holatini yangilash
            await self.set_user_online_status(True)

            # Foydalanuvchi ID asosida guruhga qo'shish
            group_name = f"user_{self.worker.id}"
            self.worker_groups.append(group_name)

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
        for group_name in self.worker_groups:
            await self.channel_layer.group_discard(
                group_name,
                self.channel_name
            )

    async def order_message(self, event):
        order_id = event.get('order_id')
        confirm_url = f"{settings.SITE_URL}/confirm_order/{order_id}/"
        message = event['message']

        # Foydalanuvchiga xabar yuborish
        await self.send(text_data=json.dumps({
            'message': message,
            'confirm_url': confirm_url
        }))

    @database_sync_to_async
    def set_user_online_status(self, status):
        """Foydalanuvchi online holatini belgilash"""
        self.worker.is_online = status
        self.worker.save()


#
# class OrderConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.user = self.scope.get('user', None)
#         self.worker_groups = []
#         self.user_channel_name = self.channel_name
#
#         # Agar foydalanuvchi mavjud bo'lmasa, ulanishni rad etish
#         if not self.user or not hasattr(self.user, 'phone'):
#             await self.close()
#             return
#
#         try:
#             # `Worker` modelidan foydalanuvchini olish
#             worker = await database_sync_to_async(AbstractUser.objects.get)(phone=self.user.phone)
#
#             await self.set_user_online_status(worker, True)
#
#             # `job_id` va `job_category` ma'lumotlarini olish
#             job_ids = await database_sync_to_async(lambda: list(worker.job_id.all()))()
#             category_id = await database_sync_to_async(
#                 lambda: worker.job_category.id if worker.job_category else None)()
#
#             # Tanlangan `category` va `job_id` mos keladigan guruhlarni yaratish va ulanish
#             if category_id:
#                 for job in job_ids:
#                     group_name = f"category_{category_id}_job_{job.id}"
#                     self.worker_groups.append(group_name)
#                     # Har bir guruhga qo'shish
#                     await self.channel_layer.group_add(
#                         group_name,
#                         self.channel_name
#                     )
#                 print(f"Guruhlar yaratildi: {self.worker_groups}, Foydalanuvchi: {self.user}")
#
#             await self.accept()
#         except AbstractUser.DoesNotExist:
#             # Agar `worker` topilmasa, ulanishni yopish
#             await self.close()
#
#     async def disconnect(self, close_code):
#         # Har bir guruhdan chiqarish
#         for group_name in self.worker_groups:
#             await self.channel_layer.group_discard(
#                 group_name,
#                 self.channel_name
#             )
#
#         if self.user:
#             worker = await database_sync_to_async(AbstractUser.objects.get)(phone=self.user.phone)
#             await self.set_user_online_status(worker, False)
#
#     async def order_message(self, event):
#         order_id = event.get('order_id')
#         confirm_url = f"{settings.SITE_URL}/confirm_order/{order_id}/"
#         messages = {
#             "text": f"{confirm_url}",
#         }
#
#         message = event['message']
#
#         # Yangi order uchun xabar yuborilishi kerak
#         if not hasattr(self, 'handled_orders'):
#             self.handled_orders = set()  # Xabar yuborilgan orderlar ro'yxati
#
#         # Agar order allaqachon yuborilgan bo'lsa, xabar yubormaslik
#         if order_id in self.handled_orders:
#             return
#
#         # Har bir guruh uchun xabar yuborish
#         for group_name in self.worker_groups:
#             # Faqat `user`ni o'z kanaliga yubormaslik
#             await self.channel_layer.group_send(
#                 group_name,
#                 {
#                     "type": "order_message",
#                     "message": message,
#                     "order_id": order_id
#                 }
#             )
#
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'messages': messages
#         }))
#
#         # Xabar yuborilgan orderlarni saqlash
#         self.handled_orders.add(order_id)
#
#     @database_sync_to_async
#     def set_user_online_status(self, user, status):
#         user.is_online = status
#         user.save()
