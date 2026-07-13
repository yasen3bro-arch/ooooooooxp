"""
سكريبت إيقاف البوت
"""
import os
import sys

def stop_bot():
    bot_dir = os.path.dirname(os.path.abspath(__file__))
    pid_file = os.path.join(bot_dir, "bot.pid")

    if not os.path.exists(pid_file):
        print("❌ لا يوجد ملف PID — البوت غير مشغّل")
        sys.exit(0)

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        os.kill(pid, 15)  # SIGTERM
        os.remove(pid_file)
        print(f"✅ تم إيقاف البوت (PID: {pid})")
    except ProcessLookupError:
        print("⚠️ البوت غير موجود (ربما أُوقف مسبقاً)")
        if os.path.exists(pid_file):
            os.remove(pid_file)
    except Exception as e:
        print(f"❌ خطأ: {e}")

    sys.exit(0)

if __name__ == "__main__":
    stop_bot()
