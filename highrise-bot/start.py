"""
سكريبت تشغيل البوت كعملية خلفية (daemon)
مخصص للاستضافة التي تتطلب انتهاء العملية الأساسية
"""
import subprocess
import sys
import os

def start_bot():
    bot_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(bot_dir, "bot.log")
    pid_file = os.path.join(bot_dir, "bot.pid")

    # إيقاف أي نسخة سابقة
    if os.path.exists(pid_file):
        try:
            with open(pid_file, 'r') as f:
                old_pid = int(f.read().strip())
            os.kill(old_pid, 0)  # فحص وجود العملية
            print(f"⚠️ البوت يعمل مسبقاً بـ PID: {old_pid}")
            print("🔄 إعادة التشغيل...")
            os.kill(old_pid, 15)  # SIGTERM
            import time
            time.sleep(2)
        except (ProcessLookupError, ValueError):
            pass  # العملية غير موجودة

    # تشغيل البوت في الخلفية
    python_exe = sys.executable
    log = open(log_file, 'a', encoding='utf-8')

    process = subprocess.Popen(
        [python_exe, "run.py"],
        cwd=bot_dir,
        stdout=log,
        stderr=subprocess.STDOUT,
        start_new_session=True  # فصل العملية عن الـ terminal
    )

    # حفظ PID
    with open(pid_file, 'w') as f:
        f.write(str(process.pid))

    print(f"✅ تم تشغيل البوت بنجاح")
    print(f"📋 PID: {process.pid}")
    print(f"📄 السجل: {log_file}")
    print(f"💡 لإيقاف البوت: python3 stop.py")

    sys.exit(0)  # الخروج بنجاح — يظهر كـ "Completed"

if __name__ == "__main__":
    start_bot()
