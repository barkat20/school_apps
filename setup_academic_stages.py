import sys
import os

# Adjust paths as needed
odoo_path = r"D:\odoo18 for\odoo"
sys.path.append(odoo_path)

import odoo

def main():
    # Initialize Odoo
    odoo.tools.config.parse_config(['-c', os.path.join(odoo_path, 'odoo.conf'), '-d', 'school_db'])
    odoo.cli.server.report_configuration()
    
    registry = odoo.registry('school_db')

    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        # 1. Academic Stages (standard.standard)
        Stage = env['standard.standard']
        
        stages_data = [
            {'en': 'Elementary school', 'fr': 'École Primaire', 'ar': 'المدرسة الابتدائية', 'code': 'ELEM', 'seq': 10},
            {'en': 'Middle school', 'fr': 'Collège', 'ar': 'المدرسة المتوسطة', 'code': 'MID', 'seq': 20},
            {'en': 'High school', 'fr': 'Lycée', 'ar': 'المدرسة الثانوية', 'code': 'HIGH', 'seq': 30},
        ]
        
        stages_map = {}
        for s in stages_data:
            rec = Stage.search([('code', '=', s['code'])])
            if not rec:
                rec = Stage.create({
                    'name': s['en'],
                    'code': s['code'],
                    'sequence': s['seq']
                })
            
            # Update translations using context
            rec.with_context(lang='ar_001').write({'name': s['ar']})
            rec.with_context(lang='fr_FR').write({'name': s['fr']})
            # Also set EN
            rec.with_context(lang='en_US').write({'name': s['en']})
            
            stages_map[s['code']] = rec.id

        # 2. Student Studying Year (standard.medium)
        Year = env['standard.medium']
        
        # Helper to create grades
        def create_grades(stage_code, max_grade, prefix_en, prefix_fr, prefix_ar, base_seq):
            for i in range(1, max_grade + 1):
                en_name = f"{i}{'st' if i==1 else 'nd' if i==2 else 'rd' if i==3 else 'th'} {prefix_en}"
                fr_name = f"{i}{'ère' if i==1 else 'ème'} {prefix_fr}"
                ar_name = f"السنة {i} {prefix_ar}"
                code = f"{stage_code}_G{i}"
                seq = base_seq + i
                
                rec = Year.search([('code', '=', code)])
                if not rec:
                    rec = Year.create({
                        'name': en_name,
                        'code': code,
                        'sequence': seq,
                        'academic_stage_id': stages_map[stage_code]
                    })
                
                rec.with_context(lang='ar_001').write({'name': ar_name})
                rec.with_context(lang='fr_FR').write({'name': fr_name})
                rec.with_context(lang='en_US').write({'name': en_name})

        # Elementary: 1st to 5th
        create_grades('ELEM', 5, 'Elementary', 'Primaire', 'ابتدائي', 100)
        # Middle: 1st to 4th
        create_grades('MID', 4, 'Middle', 'Moyen', 'متوسط', 200)
        # High: 1st to 3rd
        create_grades('HIGH', 3, 'High', 'Secondaire', 'ثانوي', 300)
        
        print("Academic Stages and Studying Years have been successfully configured and translated!")
        cr.commit()

if __name__ == '__main__':
    main()
