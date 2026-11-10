# -*- coding: utf-8 -*-

class OptimizationLogger:
    def __init__(self):
        self.logs = []
        self.operations = {
            'pull_ups': 0,
            'teacher_swaps': 0,
            'swap_chains': 0,
            'gap_recoveries': 0
        }
        self.unplaced_reasons = []
        
    def log(self, message):
        self.logs.append(message)
        
    def record_op(self, op_type):
        if op_type in self.operations:
            self.operations[op_type] += 1
            
    def record_unplaced(self, req, reason):
        self.unplaced_reasons.append(f"Missing {req['subject'].name} for {req['standard'].name}: {reason}")
        
    def generate_report(self, total_placed, total_unplaced, exec_time):
        report = [
            "=== PROFESSIONAL TIMETABLE OPTIMIZATION REPORT ===",
            f"Execution Time: {exec_time:.2f} seconds",
            f"Total Lessons Placed: {total_placed}",
            f"Total Unplaced Lessons: {total_unplaced}",
            "--- Optimization Operations ---",
            f"Pull-Up Operations (Level 1): {self.operations['pull_ups']}",
            f"Teacher Swaps (Level 2): {self.operations['teacher_swaps']}",
            f"Swap Chains Executed (Level 3): {self.operations['swap_chains']}",
            f"Gap Recoveries: {self.operations['gap_recoveries']}",
        ]
        if self.unplaced_reasons:
            report.append("--- Unplaced Reasons ---")
            report.extend(self.unplaced_reasons)
        report.append("==================================================")
        return "\n".join(report)
