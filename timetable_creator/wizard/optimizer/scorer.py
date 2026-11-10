# -*- coding: utf-8 -*-

class TimetableScorer:
    def __init__(self, engine):
        self.engine = engine
        
    def calculate_score(self, assignments_dict):
        """
        Calculates the penalty score of the timetable.
        Lower score = Better timetable.
        """
        teacher_day_slots = {}
        student_day_slots = {}
        for (ck_std, ck_d_idx, ck_s_start, ck_sub_id), ck_req in assignments_dict.items():
            t_id = ck_req['teacher'].id
            if t_id not in teacher_day_slots:
                teacher_day_slots[t_id] = {d: [] for d in self.engine.available_day_indices}
            teacher_day_slots[t_id][ck_d_idx].append((ck_s_start, ck_s_start + ck_req['block_size']))
            
            if ck_std not in student_day_slots:
                student_day_slots[ck_std] = {d: [] for d in self.engine.available_day_indices}
            student_day_slots[ck_std][ck_d_idx].append((ck_s_start, ck_s_start + ck_req['block_size']))
            
        total_penalty = 0
        
        # 1. Teacher Gaps
        for t_id, days in teacher_day_slots.items():
            for d_idx, d_slots in days.items():
                if len(d_slots) < 2: continue
                d_name = self.engine.day_names[d_idx]
                rec_s = getattr(self.engine.class_cond, f"{d_name.lower()}_end_morning") if getattr(self.engine.class_cond, f"{d_name.lower()}_study_morning") else -1
                rec_e = getattr(self.engine.class_cond, f"{d_name.lower()}_start_evening") if getattr(self.engine.class_cond, f"{d_name.lower()}_study_evening") else -1
                
                s_check = sorted(d_slots)
                day_span = s_check[-1][1] - s_check[0][0]
                active_hours = sum(e - s for s, e in s_check)
                empty_time = day_span - active_hours
                
                if rec_s != -1 and rec_e != -1 and s_check[0][0] <= rec_s and s_check[-1][1] >= rec_e:
                    empty_time -= (rec_e - rec_s)
                    
                if empty_time > 0:
                    total_penalty += empty_time * 100 # Teacher wait penalty
                    
                # Check for continuous gaps >= 2 hours
                for i in range(len(s_check) - 1):
                    gap = s_check[i+1][0] - s_check[i][1]
                    if rec_s != -1 and rec_e != -1 and s_check[i][1] <= rec_s and s_check[i+1][0] >= rec_e:
                        gap -= (rec_e - rec_s)
                    if gap >= 2.0:
                        total_penalty += 50000000 # Critical Failure
                    
                morning_slots = [s for s in s_check if rec_s == -1 or s[1] <= rec_s]
                if morning_slots:
                    morning_hrs = sum(e - s for s, e in morning_slots)
                    if morning_hrs > 0 and morning_hrs < 2.0:
                        total_penalty += 100000
                        
                afternoon_slots = [s for s in s_check if rec_e != -1 and s[0] >= rec_e]
                if afternoon_slots:
                    afternoon_hrs = sum(e - s for s, e in afternoon_slots)
                    if afternoon_hrs > 0 and afternoon_hrs < 2.0:
                        total_penalty += 100000
                        
        # 2. Student Gaps (Internal Holes & Late Starts)
        for std, days in student_day_slots.items():
            for d_idx, d_slots in days.items():
                if not d_slots: continue
                d_name = self.engine.day_names[d_idx]
                morning_start = getattr(self.engine.class_cond, f"{d_name.lower()}_start_morning")
                rec_s = getattr(self.engine.class_cond, f"{d_name.lower()}_end_morning") if getattr(self.engine.class_cond, f"{d_name.lower()}_study_morning") else -1
                rec_e = getattr(self.engine.class_cond, f"{d_name.lower()}_start_evening") if getattr(self.engine.class_cond, f"{d_name.lower()}_study_evening") else -1
                
                s_check = sorted(d_slots)
                
                day_span = s_check[-1][1] - s_check[0][0]
                active_hours = sum(e - s for s, e in s_check)
                empty_time = day_span - active_hours
                if rec_s != -1 and rec_e != -1 and s_check[0][0] <= rec_s and s_check[-1][1] >= rec_e:
                    empty_time -= (rec_e - rec_s)
                    
                if empty_time > 0:
                    total_penalty += empty_time * 1000 # Internal holes are very bad
                    
                first_start = s_check[0][0]
                if first_start > morning_start:
                    total_penalty += (first_start - morning_start) * 500 # Late starts are bad
                    
                for s, e in s_check:
                    total_penalty += (s - morning_start) * 5 # Gravity pull up
                    
        return total_penalty
