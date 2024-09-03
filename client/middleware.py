from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from urllib.parse import parse_qs

User = get_user_model()

class UserAuthMiddleware(BaseMiddleware):
    @database_sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    async def __call__(self, scope, receive, send):
        # user_id ni query string'dan olish
        query_string = parse_qs(scope["query_string"].decode())
        user_id = query_string.get("user_id", [None])[0]


        if user_id:
            user = await self.get_user_by_id(user_id)
            if user is not None:
                scope["user"] = user
            else:
                scope["user"] = AnonymousUser()  # Foydalanuvchi topilmasa
        else:
            scope["user"] = AnonymousUser()  # user_id mavjud bo'lmasa

        return await super().__call__(scope, receive, send)
