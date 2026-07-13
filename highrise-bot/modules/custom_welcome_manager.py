"""
مدير رسائل الترحيب الخاصة
يسمح للمشرفين والمالك فقط بتعديل رسالة ترحيبهم الخاصة عند دخول الغرفة
"""
import json
import os

WELCOMES_FILE = "data/custom_welcomes.json"
MAX_WELCOME_LENGTH = 150


class CustomWelcomeManager:
    def __init__(self):
        self.welcomes = self._load()
        print("💌 مدير رسائل الترحيب الخاصة جاهز")

    def _load(self) -> dict:
        try:
            if os.path.exists(WELCOMES_FILE):
                with open(WELCOMES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"خطأ في تحميل رسائل الترحيب الخاصة: {e}")
        return {}

    def _save(self) -> None:
        try:
            os.makedirs(os.path.dirname(WELCOMES_FILE), exist_ok=True)
            with open(WELCOMES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.welcomes, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"خطأ في حفظ رسائل الترحيب الخاصة: {e}")

    def set_welcome(self, user_id: str, username: str, text: str) -> str:
        text = text.strip()
        if not text:
            return "❌ اكتب نص الترحيب اللي عايزه بعد الأمر"
        if len(text) > MAX_WELCOME_LENGTH:
            return f"❌ الترحيب طويل قوي! أقصى طول {MAX_WELCOME_LENGTH} حرف"

        self.welcomes[user_id] = {"username": username, "text": text}
        self._save()
        return f"✅ تم حفظ ترحيبك الخاص:\n💬 \"{text}\"\nهيقوله البوت لما تدخل الغرفة"

    def remove_welcome(self, user_id: str) -> str:
        if user_id in self.welcomes:
            del self.welcomes[user_id]
            self._save()
            return "✅ تم حذف ترحيبك الخاص، هترجع للترحيب الافتراضي"
        return "ℹ️ مفيش ترحيب خاص محفوظ ليك أصلاً"

    def get_welcome_text(self, user_id: str) -> str | None:
        entry = self.welcomes.get(user_id)
        if entry:
            return entry.get("text")
        return None

    def get_my_welcome(self, user_id: str) -> str:
        text = self.get_welcome_text(user_id)
        if text:
            return f"💌 ترحيبك الحالي:\n\"{text}\""
        return "ℹ️ مفيش عندك ترحيب خاص محفوظ، اكتب 'اضف <النص>' عشان تضيف واحد"
