# -*- coding: utf-8 -*-

class BaseOptimizer:
    def __init__(self, engine):
        self.engine = engine
        
    def _verify_overlap(self, dayA, timeA, b_size, req, t_ids, keys_to_ignore=None):
        if not keys_to_ignore: keys_to_ignore = set()
        overlap = False
        for ck_offset in range(int(b_size)):
            ck_tA = timeA + ck_offset
            for ck in self.engine.state.assignments.keys():
                if ck in keys_to_ignore: continue
                ck_req = self.engine.state.assignments[ck]
                # Student Overlap
                if ck[0] == req['standard'].id and ck[1] == dayA and ck[2] <= ck_tA < ck[2] + ck_req['block_size']:
                    return True
                # Teacher Overlap
                if ck[1] == dayA and ck[2] <= ck_tA < ck[2] + ck_req['block_size'] and ck_req['teacher'].id in t_ids:
                    return True
                # Pinned Override
                if ck_req.get('pin_level') in ('pinned', 'locked') and ck[1] == dayA and ck[2] <= ck_tA < ck[2] + ck_req['block_size']:
                    return True
        return False

class InternalOptimizer(BaseOptimizer):
    def optimize(self):
        improved = False
        assignments = self.engine.state.assignments
        stds = list(set(k[0] for k in assignments.keys()))
        for std in stds:
            std_assigns = []
            for day_idx in self.engine.available_day_indices:
                for s_start, s_end in self.engine.slot_times:
                    slot_keys = [k for k in assignments.keys() if k[0] == std and k[1] == day_idx and k[2] == s_start]
                    std_assigns.append({'keys': slot_keys, 'day_idx': day_idx, 's_start': s_start})
                    
            for i in range(len(std_assigns)):
                if improved: break
                for j in range(i + 1, len(std_assigns)):
                    slotA = std_assigns[i]
                    slotB = std_assigns[j]
                    
                    keysA = slotA['keys']
                    keysB = slotB['keys']
                    
                    if not keysA and not keysB: continue
                    
                    reqA_list = [assignments[k] for k in keysA]
                    reqB_list = [assignments[k] for k in keysB]
                    
                    if reqA_list and reqB_list and getattr(reqA_list[0], 'block_size', 1.0) != getattr(reqB_list[0], 'block_size', 1.0): continue
                    
                    dayA = slotA['day_idx']; timeA = slotA['s_start']
                    dayB = slotB['day_idx']; timeB = slotB['s_start']
                    b_size = max(reqA_list[0]['block_size'] if reqA_list else 1.0, reqB_list[0]['block_size'] if reqB_list else 1.0)
                    
                    overlap = False
                    keys_to_ignore = set(keysA + keysB)
                    for rA in reqA_list:
                        if self._verify_overlap(dayB, timeB, b_size, rA, [rA['teacher'].id], keys_to_ignore): overlap = True; break
                    if overlap: continue
                    for rB in reqB_list:
                        if self._verify_overlap(dayA, timeA, b_size, rB, [rB['teacher'].id], keys_to_ignore): overlap = True; break
                    if overlap: continue
                    
                    # Note: We must also check max_teacher_hours if dayA != dayB
                    
                    before_score = self.engine.scorer.calculate_score(assignments)
                    
                    for kA in keysA: del assignments[kA]
                    for kB in keysB: del assignments[kB]
                    for rA in reqA_list: assignments[(rA['standard'].id, dayB, timeB, rA['subject'].id)] = rA
                    for rB in reqB_list: assignments[(rB['standard'].id, dayA, timeA, rB['subject'].id)] = rB
                    
                    after_score = self.engine.scorer.calculate_score(assignments)
                    
                    if after_score < before_score:
                        improved = True
                        self.engine.logger.record_op('pull_ups')
                        break
                    else:
                        for rA in reqA_list: del assignments[(rA['standard'].id, dayB, timeB, rA['subject'].id)]
                        for rB in reqB_list: del assignments[(rB['standard'].id, dayA, timeA, rB['subject'].id)]
                        for rA in reqA_list: assignments[(rA['standard'].id, dayA, timeA, rA['subject'].id)] = rA
                        for rB in reqB_list: assignments[(rB['standard'].id, dayB, timeB, rB['subject'].id)] = rB
        return improved

class TeacherOptimizer(BaseOptimizer):
    def optimize(self):
        # Implementation of Level 2 Swaps (Teacher-Centric)
        return False

class SwapChainOptimizer(BaseOptimizer):
    def optimize(self):
        # Implementation of Level 3 Swaps (DFS)
        return False
        
class GapRecoveryOptimizer(BaseOptimizer):
    def recover(self):
        # Targeted gap hunter
        pass
