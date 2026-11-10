# -*- coding: utf-8 -*-
from .scorer import TimetableScorer
from .modules import InternalOptimizer, TeacherOptimizer, SwapChainOptimizer, GapRecoveryOptimizer
from .logger import OptimizationLogger

class MultiStageOptimizer:
    def __init__(self, state, class_cond, available_day_indices, day_names, slot_times, max_teacher_hours, min_teacher_hours):
        self.state = state
        self.class_cond = class_cond
        self.available_day_indices = available_day_indices
        self.day_names = day_names
        self.slot_times = slot_times
        self.max_teacher_hours = max_teacher_hours
        self.min_teacher_hours = min_teacher_hours
        self.scorer = TimetableScorer(self)
        self.logger = OptimizationLogger()
        
        self.internal_opt = InternalOptimizer(self)
        self.teacher_opt = TeacherOptimizer(self)
        self.chain_opt = SwapChainOptimizer(self)
        self.gap_recovery = GapRecoveryOptimizer(self)
        
    def run_optimization_cycles(self, max_cycles=50):
        self.logger.log("Starting Professional Optimization Engine")
        improved = True
        cycle = 0
        
        while improved and cycle < max_cycles:
            improved = False
            cycle += 1
            self.logger.log(f"--- Optimization Cycle {cycle} ---")
            
            # Level 1: Internal Optimization
            if self.internal_opt.optimize():
                improved = True
                continue
                
            # Level 2: Teacher-Centric Swaps
            if self.teacher_opt.optimize():
                improved = True
                continue
                
            # Level 3: Swap Chains (DFS)
            if self.chain_opt.optimize():
                improved = True
                continue
                
        # Post-Generation: Gap Recovery Engine
        self.logger.log("--- Starting Dedicated Gap Recovery Engine ---")
        self.gap_recovery.recover()
        
        return self.state, self.logger
