import os

translations = {
    # Terms seen in screenshots
    "Admission Register": "سجل القبول",
    "Student ID": "الرقم الجامعي / المدرسي",
    "Student Name": "اسم الطالب",
    "Academic Year": "العام الدراسي",
    "Class": "الفصل",
    "School": "المدرسة",
    "Status": "الحالة",
    "Personal Information": "المعلومات الشخصية",
    "New": "جديد",
    "School Name": "اسم المدرسة",
    "CLASS INFORMATION": "معلومات الفصل",
    "Document Verified": "مستند تم التحقق منه",
    "Document Verification": "التحقق من المستندات",
    "Fees Received": "الرسوم المستلمة",
    "Cancel": "إلغاء",
    "Schedule": "الجدول الزمني",
    "Academic Configurations": "الإعدادات الأكاديمية",
    "Assign Roll Number": "تعيين رقم التسلسل",
    "Move Classes": "نقل الفصول",
    "Standards": "المراحل",
    "Classes": "الفصول",
    "Divisions": "الشُعب",
    "Class Room": "الغرفة الصفية",
    
    # Additional common School terms that might be missed
    "Gender": "الجنس",
    "Date of Birth": "تاريخ الميلاد",
    "Admission Date": "تاريخ القبول",
    "Address": "العنوان",
    "Street...": "الشارع...",
    "City": "المدينة",
    "State": "الولاية/المنطقة",
    "Country": "الدولة",
    "ZIP": "الرمز البريدي",
    "Phone Number": "رقم الهاتف",
    "Mobile Number": "رقم المحمول",
    "Email Address": "عنوان البريد الإلكتروني",
    "Medium": "اللغة/المسار",
    "Division": "الشعبة",
    "Street": "الشارع",
    "Phone": "الهاتف",
    "Mobile": "المحمول",
    "Email": "البريد الإلكتروني",
}

def translate_po(po_path):
    with open(po_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('msgid "'):
            msgid = line[7:-1]
            if msgid in translations:
                new_lines.append(line)
                i += 1
                # Replace the msgstr
                if i < len(lines) and lines[i].startswith('msgstr '):
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                else:
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                    continue
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
        
    with open(po_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


translate_po(r"d:\odoo18 for\odoo\school_apps\school\i18n\ar.po")
translate_po(r"d:\odoo18 for\odoo\school_apps\school_fees\i18n\ar.po")

print("Done updating PO with missing translations.")
