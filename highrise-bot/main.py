"""
MyBot - الكلاس الرئيسي للبوت
يُستدعى من run.py عبر: import_module("main").MyBot()
"""
import asyncio
from highrise import BaseBot, User
from highrise.models import Position, AnchorPosition, Item

from modules.user_manager import UserManager
from modules.emotes_manager import EmotesManager
from modules.responses_manager import ResponsesManager
from modules.commands_handler import CommandsHandler
from modules.position_manager import PositionManager


class MyBot(BaseBot):

    def __init__(self):
        super().__init__()

        # تهيئة جميع المديرين
        self.user_manager      = UserManager()
        self.emotes_manager    = EmotesManager()
        self.responses_manager = ResponsesManager()
        self.position_manager  = PositionManager()

        # commands_handler يحتاج self (البوت) لأنه يستخدم self.highrise
        # نؤجّل تهيئته حتى on_start حين يكون self.highrise جاهزاً
        self.commands_handler  = None

        # معلومات الاتصال (يملؤها on_start)
        self.connection_info   = {}
        self.cached_room_users = []
        self.auto_emotes       = {}   # {user_id: {"emote": str, "task": Task}}

        print("🤖 MyBot جاهز للاتصال...")

    # ─────────────────────────────────────────────
    async def on_start(self, session_metadata) -> None:
        """عند بدء الاتصال بـ Highrise"""
        try:
            self.commands_handler = CommandsHandler(self)

            self.connection_info = {
                "room_id":      session_metadata.room_info.room_id if hasattr(session_metadata, 'room_info') else "unknown",
                "user_id":      session_metadata.user_info.user_id if hasattr(session_metadata, 'user_info') else "unknown",
                "connected_at": __import__("time").time(),
            }

            print("✅ البوت متصل بالغرفة بنجاح!")
            print(f"   🏠 الغرفة: {self.connection_info.get('room_id')}")
            print(f"   🤖 معرف البوت: {self.connection_info.get('user_id')}")

            # كتابة حالة الاتصال
            try:
                with open("bot_status.txt", "w", encoding="utf-8") as f:
                    f.write(f"CONNECTED:{__import__('time').time()}\n")
                    f.write(f"ROOM_ID:{self.connection_info.get('room_id')}\n")
                    f.write(f"USER_ID:{self.connection_info.get('user_id')}\n")
            except Exception:
                pass

        except Exception as e:
            print(f"❌ خطأ في on_start: {e}")

    # ─────────────────────────────────────────────
    async def on_chat(self, user: User, message: str) -> None:
        """عند استقبال رسالة في الشات"""
        try:
            if self.commands_handler:
                result = await self.commands_handler.handle_command(user, message)
                if result:
                    await self.highrise.chat(result)
        except Exception as e:
            print(f"❌ خطأ في on_chat من {user.username}: {e}")

    # ─────────────────────────────────────────────
    async def on_whisper(self, user: User, message: str) -> None:
        """عند استقبال رسالة خاصة"""
        try:
            if self.commands_handler:
                result = await self.commands_handler.handle_command(user, message, source="whisper")
                if result:
                    await self.highrise.send_whisper(user.id, result)
        except Exception as e:
            print(f"❌ خطأ في on_whisper من {user.username}: {e}")

    # ─────────────────────────────────────────────
    async def on_user_join(self, user: User, position: Position | AnchorPosition) -> None:
        """عند دخول مستخدم جديد للغرفة"""
        try:
            user_info = await self.user_manager.add_user_to_room(user, self)
            print(f"👋 {user.username} دخل الغرفة")
            if user_info:
                print(f"   📊 النوع: {user_info.get('user_type', '؟')}")
                print(f"   👮 مشرف: {user_info.get('is_moderator', False)}")

            welcome_msg = self.responses_manager.get_welcome_response(user)
            if welcome_msg:
                await self.highrise.chat(welcome_msg)

        except Exception as e:
            print(f"❌ خطأ في معالجة دخول {user.username}: {e}")

    # ─────────────────────────────────────────────
    async def on_user_leave(self, user: User) -> None:
        """عند مغادرة مستخدم للغرفة"""
        try:
            farewell_msg = self.responses_manager.get_farewell_message(user)
            if farewell_msg:
                await self.highrise.chat(farewell_msg)
            print(f"🚪 {user.username} غادر الغرفة")

        except Exception as e:
            print(f"❌ خطأ في معالجة مغادرة {user.username}: {e}")

    # ─────────────────────────────────────────────
    async def on_user_move(self, user: User, position: Position | AnchorPosition) -> None:
        """عند تحرك مستخدم داخل الغرفة"""
        try:
            if hasattr(self.user_manager, 'update_user_position'):
                self.user_manager.update_user_position(user.id, position)
        except Exception as e:
            print(f"❌ خطأ في on_user_move: {e}")

    # ─────────────────────────────────────────────
    async def on_emote(self, user: User, emote_id: str, receiver: User | None) -> None:
        """عند تنفيذ رقصة/حركة"""
        try:
            if self.commands_handler and hasattr(self.commands_handler, 'handle_emote'):
                await self.commands_handler.handle_emote(user, emote_id, receiver)
        except Exception as e:
            print(f"❌ خطأ في on_emote: {e}")

    # ─────────────────────────────────────────────
    async def repeat_emote_for_user(self, user_id: str, emote: str) -> None:
        """تكرار الرقصة للمستخدم حتى يتم إلغاؤها"""
        try:
            while True:
                try:
                    await self.highrise.send_emote(emote, user_id)
                except Exception as e:
                    print(f"⚠️ خطأ في تكرار الرقصة: {e}")
                await asyncio.sleep(8)
        except asyncio.CancelledError:
            pass

    # ─────────────────────────────────────────────
    async def on_tip(self, sender: User, receiver: User, tip) -> None:
        """عند استقبال إكرامية"""
        try:
            if self.commands_handler and hasattr(self.commands_handler, 'handle_tip'):
                await self.commands_handler.handle_tip(sender, receiver, tip)
        except Exception as e:
            print(f"❌ خطأ في on_tip: {e}")
