import os
import shutil

translations_ar = {
    "Attendance": "الحضور",
    "Attendance (\%)": "نسبة الحضور (\%)",
    "Attendance Sheet": "سجل الحضور",
    "Attendance Sheet Line": "سطر سجل الحضور",
    "Attendances": "سجلات الحضور",
    "Attendances By Month": "الحضور حسب الشهر",
    "Absent": "غائب",
    "Present": "حاضر",
    "Absent Students": "الطلاب الغائبون",
    "Generate": "إنشاء",
    "Present": "حاضر",
    "Class": "الفصل",
    "Class Teacher": "معلم الفصل",
    "Classroom Indicator": "مؤشر الفصل الدراسي",
    "Click to mark as Absent.": "انقر للتحديد كغائب.",
    "Click to mark as Present.": "انقر للتحديد كحاضر.",
    "Daily Attendance": "الحضور اليومي",
    "Daily Attendance Information": "معلومات الحضور اليومي",
    "Daily Attendance Sheet": "سجل الحضور اليومي",
    "Daily Attendance Sheets": "سجلات الحضور اليومي",
    "Date": "التاريخ",
    "Description": "الوصف",
    "Draft": "مسودة",
    "Generate?": "إنشاء؟",
    "ID": "المعرف",
    "Monthly Attendance Report": "تقرير الحضور الشهري",
    "Monthly Attendance Sheet": "سجل الحضور الشهري",
    "Name": "الاسم",
    "Percentage": "النسبة المئوية",
    "Reason": "السبب",
    "Remark": "ملاحظة",
    "Role": "الدور",
    "Status": "الحالة",
    "Student": "الطالب",
    "Student Attendance": "حضور الطالب",
    "Student Leave Request": "طلب إجازة طالب",
    "Total Absent": "إجمالي الغياب",
    "Total Present": "إجمالي الحضور",
    "Approve": "موافقة",
    "Approved": "موافق عليه",
    "Approve Leave": "الموافقة على الإجازة",
    "Cancel": "إلغاء",
    "Cancel Leave": "إلغاء الإجازة",
    "Days": "أيام",
    "Reject": "رفض",
    "Rejected": "مرفوض",
    "Faculty": "هيئة التدريس",
    "Start Date": "تاريخ البدء",
    "End Date": "تاريخ الانتهاء",
    "Leave Details": "تفاصيل الإجازة",
    "Month": "الشهر",
    "Monthly Attendance": "الحضور الشهري",
}

translations_fr = {
    "Attendance": "Présences",
    "Attendance (\%)": "Présence (\%)",
    "Attendance Sheet": "Feuille de présence",
    "Attendance Sheet Line": "Ligne de feuille de présence",
    "Attendances": "Présences",
    "Attendances By Month": "Présences par mois",
    "Absent": "Absent",
    "Present": "Présent",
    "Absent Students": "Élèves absents",
    "Generate": "Générer",
    "Class": "Classe",
    "Class Teacher": "Professeur principal",
    "Classroom Indicator": "Indicateur de classe",
    "Click to mark as Absent.": "Cliquez pour marquer comme absent.",
    "Click to mark as Present.": "Cliquez pour marquer comme présent.",
    "Daily Attendance": "Présence quotidienne",
    "Daily Attendance Information": "Informations de présence quotidienne",
    "Daily Attendance Sheet": "Feuille de présence quotidienne",
    "Daily Attendance Sheets": "Feuilles de présence quotidiennes",
    "Date": "Date",
    "Description": "Description",
    "Draft": "Brouillon",
    "Generate?": "Générer ?",
    "ID": "ID",
    "Monthly Attendance Report": "Rapport de présence mensuel",
    "Monthly Attendance Sheet": "Feuille de présence mensuelle",
    "Name": "Nom",
    "Percentage": "Pourcentage",
    "Reason": "Raison",
    "Remark": "Remarque",
    "Role": "Rôle",
    "Status": "Statut",
    "Student": "Élève",
    "Student Attendance": "Présence de l'élève",
    "Student Leave Request": "Demande de congé d'élève",
    "Total Absent": "Total des absents",
    "Total Present": "Total des présents",
    "Approve": "Approuver",
    "Approved": "Approuvé",
    "Approve Leave": "Approuver le congé",
    "Cancel": "Annuler",
    "Cancel Leave": "Annuler le congé",
    "Days": "Jours",
    "Reject": "Rejeter",
    "Rejected": "Rejeté",
    "Faculty": "Faculté",
    "Start Date": "Date de début",
    "End Date": "Date de fin",
    "Leave Details": "Détails du congé",
    "Month": "Mois",
    "Monthly Attendance": "Présence mensuelle",
}

def translate_pot(pot_path, po_path, translations, lang_code):
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
                if i < len(lines) and lines[i].startswith('msgstr "'):
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                else:
                    new_lines.append(f'msgstr "{translations[msgid]}"')
                    continue
                i += 1
                continue
        
        if line.startswith('"Language-Team: \\n"'):
            new_lines.append(line)
            new_lines.append(f'"Language: {lang_code}\\n"')
        else:
            new_lines.append(line)
        i += 1
        
    with open(po_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))


pot_file = r"d:\odoo18 for\odoo\school_apps\school_attendance\i18n\school_attendance.pot"
ar_file = r"d:\odoo18 for\odoo\school_apps\school_attendance\i18n\ar.po"
fr_file = r"d:\odoo18 for\odoo\school_apps\school_attendance\i18n\fr.po"

translate_pot(pot_file, ar_file, translations_ar, "ar_001")
translate_pot(pot_file, fr_file, translations_fr, "fr")

print("Generated Arabic and French translation files.")
