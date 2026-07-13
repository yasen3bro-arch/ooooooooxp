
"""
أوامر VIP الخاصة - تحتوي على أوامر متقدمة للأعضاء المميزين
"""
import asyncio
from highrise import BaseBot, User, Position, AnchorPosition

class VipCommands:
    def __init__(self, bot):
        self.bot = bot
        if not hasattr(self.bot, 'vip_following_tasks'):
            self.bot.vip_following_tasks = {}
        print("💎 أوامر VIP جاهزة")

    async def handle_vip_command(self, user, message):
        """معالجة أوامر VIP"""
        try:
            # أمر الملاحقة المتقدم للـ VIP (الجديد)
            if message.startswith("follow @") or message.startswith("اتبع @") or message.startswith("لاحق @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_follow_user(user, target_username)
                else:
                    return "❌ الاستخدام: follow @اسم_المستخدم أو لاحق @اسم_المستخدم"

            elif message.startswith("stopfollow") or message == "توقف_متابعة" or message == "ايقاف_الملاحقة":
                return await self.vip_stop_follow(user)

            elif message == "followers" or message == "المتابعين" or message == "الملاحقين":
                return await self.get_vip_followers_list(user)

            elif message.startswith("lead @") or message.startswith("قود @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_lead_user(user, target_username)
                else:
                    return "❌ الاستخدام: lead @اسم_المستخدم"

            # أمر إيقاف القيادة للـ VIP
            elif message.startswith("stop_lead @") or message.startswith("الغ_قيادة @") or message.startswith("ايقاف_قيادة @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_stop_lead(user, target_username)
                else:
                    return "❌ الاستخدام: stop_lead @اسم_المستخدم أو الغ_قيادة @اسم_المستخدم"

            elif message == "stop_all_leads" or message == "ايقاف_كل_القيادات":
                return await self.vip_stop_all_leads(user)

            # أمر الغمزة الجديد للـ VIP
            elif message == "wink" or message == "غمزة":
                return await self.vip_wink(user)

            # أمر إرسال القلب لمستخدم
            elif message.startswith("h @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_send_heart(user, target_username)
                else:
                    return "❌ الاستخدام: h @اسم_المستخدم"

            # أمر إرسال غمزة لمستخدم
            elif message.startswith("غمزه @") or message.startswith("غمزة @"):
                parts = message.split()
                if len(parts) >= 2 and parts[1].startswith("@"):
                    target_username = parts[1][1:]
                    return await self.vip_send_wink(user, target_username)
                else:
                    return "❌ الاستخدام: غمزه @اسم_المستخدم"

            # أمر نقل VIP إلى الموقع المميز
            elif message == "vip":
                return await self.vip_teleport_to_spot(user)

            return None

        except Exception as e:
            print(f"❌ خطأ في معالجة أوامر VIP: {e}")
            return "❌ حدث خطأ في تنفيذ الأمر"

    async def vip_follow_user(self, user, target_username):
        """أمر الملاحقة المتقدم للـ VIP"""
        try:
            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            # التحقق من وجود ملاحقة سابقة
            if user.id in self.bot.vip_following_tasks:
                self.bot.vip_following_tasks[user.id]['task'].cancel()
                del self.bot.vip_following_tasks[user.id]

            # بدء الملاحقة
            task = asyncio.create_task(self._follow_loop(user, target_user))
            self.bot.vip_following_tasks[user.id] = {
                'task': task,
                'target_username': target_user.username,
                'target_id': target_user.id
            }

            return f"💎 بدأت متابعة @{target_user.username} بنجاح! استخدم 'stopfollow' للتوقف"

        except Exception as e:
            return f"❌ فشل في بدء الملاحقة: {str(e)}"

    async def _follow_loop(self, follower_user, target_user):
        """حلقة الملاحقة المتقدمة للـ VIP"""
        try:
            print(f"💎 بدء ملاحقة VIP: {follower_user.username} يتبع {target_user.username}")
            
            while True:
                try:
                    # الحصول على موقع المستخدم المستهدف
                    room_users = await self.bot.highrise.get_room_users()
                    target_position = None
                    
                    for room_user, position in room_users.content:
                        if room_user.id == target_user.id:
                            target_position = position
                            break
                    
                    if target_position is None:
                        # المستخدم المستهدف غادر الغرفة
                        await self.bot.highrise.send_whisper(
                            follower_user.id, 
                            f"💎 توقفت المتابعة - @{target_user.username} غادر الغرفة"
                        )
                        break
                    
                    # تحريك البوت بجانب المستخدم المستهدف
                    if type(target_position) != AnchorPosition:
                        # حساب موقع محسن بجانب المستخدم
                        follow_position = Position(
                            target_position.x + 1.0,  # بجانب المستخدم
                            target_position.y,
                            target_position.z
                        )
                        
                        await self.bot.highrise.walk_to(follow_position)
                    
                    # تأخير أقل للاستجابة السريعة
                    await asyncio.sleep(0.3)
                
                except Exception as e:
                    print(f"⚠️ خطأ في حلقة ملاحقة VIP: {e}")
                    await asyncio.sleep(1)
                    continue
                    
        except asyncio.CancelledError:
            print(f"💎 تم إلغاء ملاحقة VIP: {follower_user.username}")
        except Exception as e:
            print(f"❌ خطأ في ملاحقة VIP: {e}")
            await self.bot.highrise.send_whisper(
                follower_user.id, 
                f"❌ حدث خطأ في المتابعة: {str(e)}"
            )

    async def vip_stop_follow(self, user):
        """إيقاف الملاحقة للـ VIP"""
        try:
            if user.id not in self.bot.vip_following_tasks:
                return "❌ أنت لا تتابع أي شخص حالياً"
            
            # إلغاء المهمة
            self.bot.vip_following_tasks[user.id]['task'].cancel()
            target_username = self.bot.vip_following_tasks[user.id]['target_username']
            del self.bot.vip_following_tasks[user.id]
            
            return f"💎 تم إيقاف متابعة @{target_username} بنجاح"
            
        except Exception as e:
            return f"❌ فشل في إيقاف المتابعة: {str(e)}"

    async def get_vip_followers_list(self, user):
        """قائمة المتابعين الحاليين للـ VIP"""
        try:
            if not self.bot.vip_following_tasks:
                return "❌ لا يوجد أعضاء VIP يتابعون أحد حالياً"
            
            followers_list = []
            for follower_id, data in self.bot.vip_following_tasks.items():
                # الحصول على اسم المتابع
                room_users = await self.bot.highrise.get_room_users()
                follower_name = "مجهول"
                
                for room_user, _ in room_users.content:
                    if room_user.id == follower_id:
                        follower_name = room_user.username
                        break
                
                followers_list.append(f"💎 {follower_name} ← {data['target_username']}")
            
            if followers_list:
                return f"📋 قائمة متابعات VIP ({len(followers_list)}):\n" + "\n".join(followers_list)
            else:
                return "❌ لا يوجد متابعات VIP نشطة"
                
        except Exception as e:
            return f"❌ خطأ في جلب قائمة المتابعين: {str(e)}"

    async def vip_lead_user(self, user, target_username):
        """أمر قيادة متقدم للـ VIP - يجعل المستخدم المستهدف يتبع الـ VIP"""
        try:
            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            # إنشاء مهمة قيادة
            task_key = f"lead_{target_user.id}"
            if hasattr(self.bot, 'vip_lead_tasks') and task_key in self.bot.vip_lead_tasks:
                self.bot.vip_lead_tasks[task_key]['task'].cancel()
            
            if not hasattr(self.bot, 'vip_lead_tasks'):
                self.bot.vip_lead_tasks = {}

            task = asyncio.create_task(self._lead_loop(user, target_user))
            self.bot.vip_lead_tasks[task_key] = {
                'task': task,
                'leader_username': user.username,
                'target_username': target_user.username
            }

            return f"💎 الآن @{target_user.username} يتبعك! استخدم 'stop_lead @{target_username}' للتوقف"

        except Exception as e:
            return f"❌ فشل في بدء القيادة: {str(e)}"

    async def _lead_loop(self, leader_user, target_user):
        """حلقة القيادة - جعل المستخدم يتبع الـ VIP"""
        try:
            print(f"💎 بدء قيادة VIP: {target_user.username} يتبع {leader_user.username}")
            
            while True:
                try:
                    # الحصول على موقع القائد (VIP)
                    room_users = await self.bot.highrise.get_room_users()
                    leader_position = None
                    target_exists = False
                    
                    for room_user, position in room_users.content:
                        if room_user.id == leader_user.id:
                            leader_position = position
                        if room_user.id == target_user.id:
                            target_exists = True
                    
                    if not target_exists:
                        # المستخدف المستهدف غادر
                        break
                    
                    if leader_position and type(leader_position) != AnchorPosition:
                        # نقل المستخدم المستهدف بجانب القائد
                        follow_position = Position(
                            leader_position.x - 1.0,  # خلف القائد
                            leader_position.y,
                            leader_position.z
                        )
                        
                        await self.bot.highrise.teleport(target_user.id, follow_position)
                    
                    await asyncio.sleep(0.5)
                
                except Exception as e:
                    print(f"⚠️ خطأ في حلقة قيادة VIP: {e}")
                    await asyncio.sleep(1)
                    continue
                    
        except asyncio.CancelledError:
            print(f"💎 تم إلغاء قيادة VIP")
        except Exception as e:
            print(f"❌ خطأ في قيادة VIP: {e}")

    async def vip_stop_lead(self, user, target_username):
        """إيقاف قيادة مستخدم محدد"""
        try:
            if not hasattr(self.bot, 'vip_lead_tasks'):
                return "❌ لا توجد مهام قيادة نشطة"

            # البحث عن المستخدم المستهدف
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                return f"❌ لم يتم العثور على المستخدم @{target_username} في الغرفة"

            task_key = f"lead_{target_user.id}"
            
            if task_key not in self.bot.vip_lead_tasks:
                return f"❌ المستخدم @{target_username} غير مقود حالياً"
            
            # إلغاء مهمة القيادة
            self.bot.vip_lead_tasks[task_key]['task'].cancel()
            del self.bot.vip_lead_tasks[task_key]
            
            print(f"💎 تم إيقاف قيادة VIP لـ {target_username}")
            return f"💎 تم إيقاف قيادة @{target_username} بنجاح"
            
        except Exception as e:
            print(f"❌ خطأ في إيقاف قيادة VIP: {e}")
            return f"❌ فشل في إيقاف القيادة: {str(e)}"

    async def vip_stop_all_leads(self, user):
        """إيقاف جميع مهام القيادة"""
        try:
            if not hasattr(self.bot, 'vip_lead_tasks') or not self.bot.vip_lead_tasks:
                return "❌ لا توجد مهام قيادة نشطة"

            stopped_count = 0
            stopped_users = []
            
            # إيقاف جميع مهام القيادة
            for task_key, data in list(self.bot.vip_lead_tasks.items()):
                try:
                    data['task'].cancel()
                    stopped_users.append(data['target_username'])
                    stopped_count += 1
                except Exception as e:
                    print(f"❌ خطأ في إيقاف مهمة القيادة {task_key}: {e}")
            
            # مسح جميع المهام
            self.bot.vip_lead_tasks.clear()
            
            if stopped_count > 0:
                users_list = ", ".join(stopped_users[:3])
                if len(stopped_users) > 3:
                    users_list += f" و {len(stopped_users) - 3} آخرين"
                
                print(f"💎 تم إيقاف {stopped_count} مهمة قيادة VIP")
                return f"💎 تم إيقاف جميع مهام القيادة ({stopped_count}):\n📋 المستخدمين: {users_list}"
            else:
                return "❌ لم يتم إيقاف أي مهام قيادة"
                
        except Exception as e:
            print(f"❌ خطأ في إيقاف جميع مهام القيادة VIP: {e}")
            return f"❌ فشل في إيقاف جميع القيادات: {str(e)}"

    async def vip_wink(self, user):
        """أمر الغمزة الخاص بـ VIP"""
        try:
            # تنفيذ حركة الغمزة
            await self.bot.highrise.send_emote("emote-lust", user.id)
            
            # إرسال رسالة في الشات العام للتأثير
            await self.bot.highrise.chat(f"😉 {user.username} يرسل غمزة مميزة! 💎")
            
            print(f"💎 تم تنفيذ أمر الغمزة VIP بواسطة {user.username}")
            return "😉💎 تم إرسال الغمزة المميزة بنجاح!"
            
        except Exception as e:
            print(f"❌ خطأ في تنفيذ الغمزة VIP: {e}")
            return "❌ فشل في تنفيذ الغمزة، جرب مرة أخرى"

    async def vip_send_heart(self, user, target_username: str):
        """إرسال تفاعل قلب لمستخدم مستهدف"""
        try:
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break

            if not target_user:
                return f"❌ لم يتم العثور على @{target_username} في الغرفة"

            print(f"💕 {user.username} يرسل قلوب لـ {target_username}")

            for i in range(30):
                await self.bot.highrise.react("heart", target_user.id)
                await asyncio.sleep(0.1)

            print(f"💕 تم إرسال قلوب لـ {target_username}")
            return f"💕 تم إرسال قلوب لـ @{target_username}!"

        except Exception as e:
            print(f"❌ خطأ في إرسال القلب: {e}")
            return "❌ فشل في إرسال القلب"

    async def vip_send_wink(self, user, target_username: str):
        """إرسال تفاعل غمزة لمستخدم مستهدف"""
        try:
            room_users = await self.bot.highrise.get_room_users()
            target_user = None
            for room_user, _ in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break

            if not target_user:
                return f"❌ لم يتم العثور على @{target_username} في الغرفة"

            print(f"😉 {user.username} يرسل غمزة لـ {target_username}")

            for i in range(30):
                await self.bot.highrise.react("wink", target_user.id)
                await asyncio.sleep(0.1)

            print(f"😉 تم إرسال غمزة لـ {target_username}")
            return f"😉 تم إرسال غمزة لـ @{target_username}!"

        except Exception as e:
            print(f"❌ خطأ في إرسال الغمزة: {e}")
            return "❌ فشل في إرسال الغمزة"

    async def vip_teleport_to_spot(self, user):
        """نقل VIP إلى الموقع المميز"""
        try:
            from highrise import Position
            vip_position = Position(16.0, 19.0, 28.0)
            await self.bot.highrise.teleport(user.id, vip_position)
            print(f"💎 تم نقل {user.username} إلى موقع VIP")
            return "💎✨ مرحباً في منطقة VIP!"

        except Exception as e:
            print(f"❌ خطأ في نقل VIP: {e}")
            return "❌ فشل في النقل إلى موقع VIP"
