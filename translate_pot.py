import os

translations = {
    "School": "المدرسة",
    "Student": "الطالب",
    "Information": "معلومات",
    "School Information": "معلومات المدرسة",
    "Student Information": "معلومات الطالب",
    "Name": "الاسم",
    "First Name": "الاسم الأول",
    "Middle Name": "الاسم الأوسط",
    "Last Name": "الاسم الأخير",
    "Birthdate": "تاريخ الميلاد",
    "Gender": "الجنس",
    "Address": "العنوان",
    "Street": "الشارع",
    "Street...": "الشارع...",
    "City": "المدينة",
    "State": "الولاية/المنطقة",
    "ZIP": "الرمز البريدي",
    "Country": "الدولة",
    "Phone": "الهاتف",
    "Phone Number": "رقم الهاتف",
    "Mobile": "المحمول",
    "Mobile Number": "رقم المحمول",
    "Email": "البريد الإلكتروني",
    "Email Address": "عنوان البريد الإلكتروني",
    "Terminate": "إنهاء",
    "Alumni": "خريج",
    "Done": "تم",
    "Standard": "المرحلة/الصف",
    "Division": "الشعبة",
    "Medium": "اللغة/المسار",
    "Class Teacher": "معلم الفصل",
    "Code": "الرمز",
    "Date": "التاريخ",
    "Description": "الوصف",
    "Sequence": "التسلسل",
    "Academic Year": "العام الدراسي",
    "Academic Years": "الأعوام الدراسية",
    "Month": "الشهر",
    "Months": "الأشهر",
    "Subject": "المادة",
    "Subjects": "المواد",
    "Syllabus": "المنهج",
    "Start Date": "تاريخ البدء",
    "End Date": "تاريخ الانتهاء",
    "Stop Date": "تاريخ الانتهاء",
    "Capacity": "السعة الاستيعابية",
    "Total Students": "إجمالي الطلاب",
    "Remaining Seats": "المقاعد المتبقية",
    "Parents": "أولياء الأمور",
    "Parent": "ولي الأمر",
    "Teacher": "المعلم",
    "Religion/Caste": "الديانة/العرق",
    "Mother Tounge": "اللغة الأم",
    "Emergency Contact Details": "بيانات التواصل عند الطوارئ",
    "Medical": "البيانات الطبية",
    "Blood Group": "فصيلة الدم",
    "Height": "الطول",
    "Weight": "الوزن",
    "Admission Date": "تاريخ القبول",
    "Leave Date": "تاريخ المغادرة",
    "History": "السجل",
    "Result": "النتيجة",
    "Percentage": "النسبة المئوية",
    "Certificates": "الشهادات",
    "Award Info": "معلومات الجوائز",
    "Family Info": "معلومات العائلة",
    "Previous School": "المدرسة السابقة",
    "References": "المراجع",
    "Remarks": "الملاحظات",
    "Fees": "الرسوم",
    "Fees Management": "إدارة الرسوم",
    "Fees Structure": "هيكل الرسوم",
    "Fees Receipts": "إيصالات الرسوم",
    "Fees Receipt": "إيصال الرسوم",
    "Fees Registers": "سجلات الرسوم",
    "Fees Register": "سجل الرسوم",
    "Fees Head": "بند الرسوم",
    "Student Payslip": "إيصال الطالب",
    "Student Payslip Line": "سطر إيصال الطالب",
    "Amount": "المبلغ",
    "Total": "الإجمالي",
    "Paid Amount": "المبلغ المدفوع",
    "Due Amount": "المبلغ المستحق",
    "Confirm": "تأكيد",
    "Payment": "الدفع",
    "Invoice": "فاتورة",
    "Draft": "مسودة",
    "Pending": "قيد الانتظار",
    "Paid": "مدفوع",
    "Journal": "دفتر اليومية",
    "Currency": "العملة",
    "Calculations": "الحسابات",
    "Function": "دالة",
    "Range": "نطاق",
    "Account": "الحساب",
    "Type": "النوع",
    "Number": "الرقم",
    "Payment Date": "تاريخ الدفع",
    "Admission": "القبول",
    "Profiles": "الملفات الشخصية",
    "Attendance": "الحضور",
    "Configuration": "الإعدادات",
    "Student ID": "الرقم الجامعي / المدرسي",
    "Admission Register": "سجل القبول",
    "Student Name": "اسم الطالب",
    "Class": "الفصل",
}

def translate_pot(pot_path, po_path):
    with open(pot_path, "r", encoding="utf-8") as f:
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
                # The next line should be msgstr ""
                if i < len(lines) and lines[i].startswith('msgstr '):
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                else:
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                    continue # we didn't consume next line if not msgstr
                i += 1
                continue
        
        if line.startswith('"Language-Team: \\n"'):
            new_lines.append(line)
            new_lines.append('"Language: ar_001\\n"')
        else:
            new_lines.append(line)
        i += 1
        
    with open(po_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


translate_pot(r"d:\odoo18 for\odoo\school_apps\school\i18n\school.pot", r"d:\odoo18 for\odoo\school_apps\school\i18n\ar.po")
translate_pot(r"d:\odoo18 for\odoo\school_apps\school_fees\i18n\school_fees.pot", r"d:\odoo18 for\odoo\school_apps\school_fees\i18n\ar.po")

print("Done translating POT to PO.")
