
"""
مدير الأماكن - نظام حفظ واستدعاء أماكن البوت
"""
import json
import os
from datetime import datetime
from highrise import Position, AnchorPosition

class PositionManager:
    def __init__(self):
        self.data_file = "data/positions_data.json"
        self.positions = {}
        self.load_positions_data()
        print("📍 مدير الأماكن جاهز")

    def load_positions_data(self):
        """تحميل بيانات الأماكن المحفوظة"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
                print(f"📂 تم تحميل {len(self.positions)} مكان محفوظ")
            else:
                os.makedirs("data", exist_ok=True)
                self.positions = {}
        except Exception as e:
            print(f"❌ خطأ في تحميل بيانات الأماكن: {e}")
            self.positions = {}

    def save_positions_data(self):
        """حفظ بيانات الأماكن"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.positions, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ خطأ في حفظ بيانات الأماكن: {e}")

    def position_to_dict(self, position):
        """تحويل Position إلى dictionary"""
        if isinstance(position, Position):
            # التعامل مع facing بشكل آمن
            facing_name = "FrontRight"  # القيمة الافتراضية
            if hasattr(position, 'facing') and position.facing:
                if hasattr(position.facing, 'name'):
                    facing_name = position.facing.name
                elif isinstance(position.facing, str):
                    facing_name = position.facing
                else:
                    # تحويل enum إلى string
                    facing_name = str(position.facing).split('.')[-1]
            
            # التأكد من أن القيمة صحيحة
            valid_facings = ["FrontRight", "FrontLeft", "BackRight", "BackLeft"]
            if facing_name not in valid_facings:
                facing_name = "FrontRight"
            
            return {
                "type": "Position",
                "x": position.x,
                "y": position.y,
                "z": position.z,
                "facing": facing_name
            }
        elif isinstance(position, AnchorPosition):
            return {
                "type": "AnchorPosition",
                "entity_id": position.entity_id,
                "anchor_ix": position.anchor_ix
            }
        return None

    def dict_to_position(self, pos_dict):
        """تحويل dictionary إلى Position"""
        try:
            from highrise import Position, AnchorPosition
            from highrise.models import Facing
        except ImportError:
            try:
                from highrise.models import Position, AnchorPosition, Facing
            except ImportError:
                print("❌ فشل في استيراد مكتبة Highrise")
                return None
        
        try:
            # التحقق من وجود المفتاح type
            if not isinstance(pos_dict, dict):
                print(f"❌ خطأ: pos_dict ليس dictionary: {type(pos_dict)}")
                return None
            
            # دعم التنسيق القديم (بدون type) والجديد (مع type)
            pos_type = pos_dict.get("type", "Position")  # افتراض Position إذا لم يكن موجود
            
            if pos_type == "Position" or "type" not in pos_dict:
            
            # التحقق من وجود الإحداثيات المطلوبة
                required_keys = ["x", "y", "z"]
                for key in required_keys:
                    if key not in pos_dict:
                        print(f"❌ خطأ: مفتاح '{key}' غير موجود في بيانات الموقع")
                        return None
                
                # تصحيح التعامل مع facing بشكل آمن
                facing_name = pos_dict.get("facing", "FrontRight")
                
                # قائمة القيم الصحيحة لـ Facing
                valid_facings = ["FrontRight", "FrontLeft", "BackLeft", "BackRight"]
                
                # تحويل القيم القديمة أو الخاطئة إلى قيم صحيحة
                facing_mapping = {
                    "FrontLeft": "FrontRight", 
                    "BackLeft": "BackRight",
                    "Left": "FrontRight",
                    "Right": "FrontRight"
                }
                
                if facing_name in facing_mapping:
                    facing_name = facing_mapping[facing_name]
                elif facing_name not in valid_facings:
                    print(f"⚠️ قيمة facing غير صحيحة: {facing_name}, استخدام FrontRight")
                    facing_name = "FrontRight"
                
                # إنشاء facing object بشكل آمن
                try:
                    # محاولة الحصول على Facing من الـ enum
                    if facing_name == "FrontRight":
                        facing = Facing.FrontRight
                    elif facing_name == "FrontLeft":
                        facing = Facing.FrontLeft  
                    elif facing_name == "BackLeft":
                        facing = Facing.BackLeft
                    elif facing_name == "BackRight":
                        facing = Facing.BackRight
                    else:
                        facing = Facing.FrontRight
                        
                except (AttributeError, NameError) as e:
                    print(f"⚠️ خطأ في إنشاء Facing: {e}, استخدام القيمة الافتراضية")
                    # استخدام facing بشكل مباشر كـ string إذا فشل enum
                    facing = "FrontRight"
                
                return Position(
                    x=float(pos_dict["x"]),
                    y=float(pos_dict["y"]), 
                    z=float(pos_dict["z"]),
                    facing=facing
                )
            elif pos_dict["type"] == "AnchorPosition":
                if "entity_id" not in pos_dict or "anchor_ix" not in pos_dict:
                    print(f"❌ خطأ: بيانات AnchorPosition غير مكتملة")
                    return None
                    
                return AnchorPosition(
                    entity_id=pos_dict["entity_id"],
                    anchor_ix=pos_dict["anchor_ix"]
                )
            else:
                print(f"❌ خطأ: نوع موقع غير مدعوم: {pos_dict['type']}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في تحويل البيانات إلى Position: {e}")
            print(f"البيانات المرسلة: {pos_dict}")
            print(f"نوع الخطأ: {type(e).__name__}")
            
            # محاولة إنشاء Position بقيم افتراضية إذا كانت البيانات الأساسية موجودة
            if isinstance(pos_dict, dict) and ("x" in pos_dict and "y" in pos_dict and "z" in pos_dict):
                try:
                    print(f"🔧 محاولة إنشاء Position احتياطي من البيانات: {pos_dict}")
                    return Position(
                        x=float(pos_dict.get("x", 0)),
                        y=float(pos_dict.get("y", 0)), 
                        z=float(pos_dict.get("z", 0)),
                        facing="FrontRight"  # استخدام string مباشرة
                    )
                except Exception as fallback_error:
                    print(f"❌ فشل في إنشاء Position احتياطي: {fallback_error}")
                    # محاولة أخيرة بدون facing
                    try:
                        return Position(
                            x=float(pos_dict.get("x", 0)),
                            y=float(pos_dict.get("y", 0)), 
                            z=float(pos_dict.get("z", 0))
                        )
                    except Exception as final_error:
                        print(f"❌ فشل نهائي في إنشاء Position: {final_error}")
            
            return None

    async def save_current_position(self, highrise, username: str, position_name: str = "default", bot_id: str = None):
        """حفظ المكان الحالي للبوت"""
        try:
            # الحصول على معلومات البوت
            room_users = (await highrise.get_room_users()).content
            bot_user = None
            bot_position = None
            
            for user, position in room_users:
                if bot_id and user.id == bot_id:
                    bot_user = user
                    bot_position = position
                    break
                elif not bot_id and hasattr(highrise, 'my_id') and user.id == highrise.my_id:
                    bot_user = user
                    bot_position = position
                    break
            
            # fallback: أول مستخدم يطابق أي ID متاح من config
            if not bot_user:
                try:
                    from config import get_bot_id
                    config_bot_id = get_bot_id()
                    for user, position in room_users:
                        if user.id == config_bot_id:
                            bot_user = user
                            bot_position = position
                            break
                except Exception:
                    pass
            
            if bot_user and bot_position:
                # تحويل المكان إلى dict
                pos_dict = self.position_to_dict(bot_position)
                if pos_dict:
                    # حفظ المكان
                    self.positions[position_name] = {
                        "position": pos_dict,
                        "saved_by": username,
                        "saved_at": datetime.now().isoformat(),
                        "description": f"تم حفظه بواسطة {username}"
                    }
                    self.save_positions_data()
                    return f"✅ تم حفظ المكان '{position_name}' بنجاح"
                else:
                    return "❌ فشل في تحويل بيانات المكان"
            else:
                return "❌ لم أتمكن من العثور على موقع البوت"
                
        except Exception as e:
            print(f"❌ خطأ في حفظ المكان: {e}")
            return f"❌ خطأ في حفظ المكان: {str(e)}"

    async def teleport_to_saved_position(self, highrise, position_name: str = "default", bot_id: str = None):
        """الانتقال إلى مكان محفوظ"""
        try:
            if position_name not in self.positions:
                available_positions = list(self.positions.keys())
                if available_positions:
                    return f"❌ المكان '{position_name}' غير موجود\n📍 الأماكن المتاحة: {', '.join(available_positions)}"
                else:
                    return "❌ لا توجد أماكن محفوظة"
            
            pos_data = self.positions[position_name]
            print(f"🔍 بيانات المكان المحفوظ: {pos_data}")
            
            if "position" not in pos_data:
                return f"❌ بيانات المكان '{position_name}' تالفة - لا يوجد مفتاح 'position'"
            
            position = self.dict_to_position(pos_data["position"])
            
            if position:
                # تحديد ID البوت بالترتيب: المُمرَّر → highrise.my_id → config
                target_id = bot_id
                if not target_id and hasattr(highrise, 'my_id'):
                    target_id = highrise.my_id
                if not target_id:
                    try:
                        from config import get_bot_id
                        target_id = get_bot_id()
                    except Exception:
                        pass
                
                if not target_id:
                    return "❌ لم يتم العثور على معرف البوت"
                
                await highrise.teleport(target_id, position)
                return f"✅ تم الانتقال إلى '{position_name}'"
            else:
                return f"❌ فشل في تحويل بيانات المكان '{position_name}'"
                
        except Exception as e:
            print(f"❌ خطأ في الانتقال: {e}")
            print(f"البيانات: {self.positions.get(position_name, 'غير موجود')}")
            return f"❌ خطأ في الانتقال: {str(e)}"

    def get_saved_positions_list(self) -> str:
        """الحصول على قائمة الأماكن المحفوظة"""
        if not self.positions:
            return "📍 لا توجد أماكن محفوظة"
        
        result = "📍 الأماكن المحفوظة:\n"
        for i, (name, data) in enumerate(self.positions.items(), 1):
            saved_date = data["saved_at"][:10]
            result += f"{i}. {name} - حفظه {data['saved_by']} ({saved_date})\n"
        
        result += f"\n💡 استخدم 'اذهب [رقم]' أو 'اذهب [اسم]' للانتقال"
        return result.strip()

    def delete_saved_position(self, position_name: str) -> str:
        """حذف مكان محفوظ"""
        if position_name not in self.positions:
            return f"❌ المكان '{position_name}' غير موجود"
        
        del self.positions[position_name]
        self.save_positions_data()
        return f"✅ تم حذف المكان '{position_name}'"

    def get_positions_count(self) -> int:
        """عدد الأماكن المحفوظة"""
        return len(self.positions)

    def fix_corrupted_positions(self) -> str:
        """إصلاح البيانات التالفة في الأماكن المحفوظة"""
        try:
            fixed_count = 0
            corrupted_positions = []
            
            for name, data in self.positions.items():
                try:
                    if "position" not in data:
                        corrupted_positions.append(name)
                        continue
                        
                    pos_dict = data["position"]
                    
                    # محاولة تحويل البيانات للتأكد من صحتها
                    test_position = self.dict_to_position(pos_dict)
                    if test_position is None:
                        corrupted_positions.append(name)
                        
                except Exception as e:
                    print(f"خطأ في فحص المكان {name}: {e}")
                    corrupted_positions.append(name)
            
            # حذف الأماكن التالفة
            for corrupted_name in corrupted_positions:
                del self.positions[corrupted_name]
                fixed_count += 1
                print(f"🗑️ تم حذف المكان التالف: {corrupted_name}")
            
            if fixed_count > 0:
                self.save_positions_data()
                return f"🔧 تم إصلاح {fixed_count} مكان تالف"
            else:
                return "✅ جميع الأماكن المحفوظة سليمة"
                
        except Exception as e:
            print(f"❌ خطأ في إصلاح البيانات: {e}")
            return f"❌ خطأ في إصلاح البيانات: {str(e)}"
