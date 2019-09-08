import random
from enum import Enum

import numpy as np


FIND = 'find'

class IdGen(object):
    def __init__(self):
        self._val = 0

    def __call__(self):
        self._val += 1
        return self._val

bug_id = IdGen()

class Bug():
    def __init__(self, btype):
        self.id = bug_id()
        self.type = btype
        self.impact = 7 if btype[0] is 'h' else 1
        self.time = 5 if btype[1] is 'h' else 2
        self.assigned = False
    
    def __repr__(self):
        return f'Bug({self.type}).{self.id}'



class Staff():
    def __init__(self, id, task=FIND):
        self.id = id
        self.task = FIND
        self.progress = 0

    def __repr__(self):
        return f'Staff().{self.id}'


# Likely number of bugs found in 1 hour at time x.
fb = lambda x:  54.6315 * np.e ** (-0.165555 * x / 25) / 25


class DefectSim():
    def __init__(self, tasks=(None, None, None)):
        # Create deterministicly random bugs to be found.
        self.bugs = []
        for i in range(55):
            self.bugs.append(Bug('hh'))
            self.bugs.append(Bug('he'))
            self.bugs.append(Bug('lh'))
            self.bugs.append(Bug('le'))
            self.bugs.append(Bug('le'))
            self.bugs.append(Bug('le'))
        random.seed(1)
        random.shuffle(self.bugs)
        # Bug lists
        self.backlog = []
        self.fixed = []
        # Simulation state
        self.timestep = 0
        self.finding_time = 0
        # Simulation statistics
        self.backlog_hist = {'hh': [], 'he': [], 'lh': [], 'le': [], 'total': []}
        self.fixed_hist = {'hh': [], 'he': [], 'lh': [], 'le': [], 'total': []}
        self.backlog_impact_hist = []
        self.total_impact_hist = []
        self.time_to_fix_hist = []
        self.found_fixed_ratio_hist = []
        # Init staff
        self.staff = (Staff(0), Staff(1), Staff(2))
        for i in range(3):
            self.staff[i].task = tasks[i]

        
    def backlog_impact(self):
        return sum(x.impact for x in self.backlog)
    
    def total_impact(self):
        unfound = sum(x.impact for x in self.bugs)
        backlog = sum(x.impact for x in self.backlog)
        return unfound + backlog

    def time_to_fix(self):
        return sum(x.time for x in self.backlog)

    def found_fixed_ratio(self):
        fixed = len(self.fixed)
        found = len(self.fixed) + len(self.backlog)
        return fixed / found
        
    def unassigned_backlog(self):
        return [b for b in self.backlog if not b.assigned]
            
    def unassigned_backlog_type(self, btype):
        return [b for b in self.backlog if b.assigned == False and b.type in btype]
    
    def append_hist_type(self, btype):
        n = len([b for b in self.backlog if b.type == btype])
        self.backlog_hist[btype].append(n)
        n = len([b for b in self.fixed if b.type == btype])
        self.fixed_hist[btype].append(n)
        
    def append_hist(self):
        for btype in ['hh', 'he', 'lh', 'le']:
            self.append_hist_type(btype)
        n = len(self.backlog)
        
        self.backlog_hist['total'].append(n)
        n = len(self.fixed)
        self.fixed_hist['total'].append(n)
        
        self.backlog_impact_hist.append(self.backlog_impact())
        self.total_impact_hist.append(self.total_impact())
        self.time_to_fix_hist.append(self.time_to_fix())
        self.found_fixed_ratio_hist.append(self.found_fixed_ratio())

        
    def add_found_bugs(self, bugs_found):
        for _ in range(int(bugs_found)):
            bug = self.bugs.pop()
            self.backlog.append(bug)
 
    def find_bugs(self, staff):
        if staff.task is not FIND:
            staff.task = FIND
            staff.progress = 0
        bugs = staff.progress + fb(self.finding_time)
        self.finding_time += 1
        staff.progress = bugs % 1
        self.add_found_bugs(bugs // 1)

    def sort_backlog(self):
            self.backlog.sort(key=self.sort_keys)
        
    def assign_bug(self, staff, bug):
        staff.task = bug
        staff.progress = 0
        bug.assigned = True
        
    def fix_bug(self, staff):
        if type(staff.task) is not Bug:
            raise ValueError('staff.task must be type Bug.')
        bug = staff.task
        staff.progress += 1
        if staff.progress == bug.time:
            self.backlog.remove(bug)
            self.fixed.append(bug)
            staff.task = None
        
    def work(self, staff):
        if staff.task is None:
            raise ValueError(f'{staff} unassigned work')

        if staff.task is FIND:
            self.find_bugs(staff)
        elif type(staff.task) is Bug:
            self.fix_bug(staff)
        
            
    def assign_task(self, staff, bugs=['hh', 'he', 'lh', 'le']):
        """
            If there are unassigned bugs in backlog assign staff to fix.
            optional param 'bugs': only fix bugs of listed types.
        """
        def assign_find(staff):
            if staff.task != FIND:
                staff.progress = 0
            staff.task = FIND
        self.sort_backlog()
        unassigned_backlog = self.unassigned_backlog_type(bugs)
        if len(unassigned_backlog) > 0:
            bug = unassigned_backlog[0]
            if bug.type in bugs:
                self.assign_bug(staff, bug)
            else:
                assign_find(staff)
        else:
            assign_find(staff)
    
    def tick(self, strat):
        if strat == 1:
            self.tick_strat1()
        elif strat == 2:
            self.tick_strat2()
        elif strat == 3:
            self.tick_strat3()

        for staff in self.staff:
            self.work(staff)
        self.timestep += 1
        self.append_hist()

    def tick_strat1(self):
        """
            Strategy 1:
            * staff 1 500hr find, staff 2 & 3 500hr fix ea.
            * Fix HE, HH, LE, LH.
        """
        self.sort_keys = lambda bug: (- bug.impact, bug.time)
        for staff in self.staff:
            if staff.id == 0: # Staff 0 always find
                if staff.task == None:
                    staff.task = FIND
            if staff.id == 1: # staff 2 always fix
                if type(staff.task) is not Bug:
                    self.assign_task(staff)
            if staff.id == 2: # Staff 2 always fix
                if type(staff.task) is not Bug:
                    self.assign_task(staff)

    def tick_strat2(self):
        """
            Strategy 2:
            * staff 1 500hr find, staff 2 250hr find 250hr fix, staff 3 500hr fix.
            * Fix HE, HH, LE, LH.
        """
        self.sort_keys = lambda bug: (- bug.impact, bug.time)
        for staff in self.staff:
            if staff.id == 0: # Staff 0 always find
                if staff.task == None:
                    staff.task = FIND
            if staff.id == 1: # staff 1 fix after 250 hours
                if self.timestep > 250 and type(staff.task) is not Bug:
                    self.assign_task(staff)
                elif staff.task == None:
                    staff.task = FIND
            if staff.id == 2: # Staff 2 always fix
                if type(staff.task) is not Bug:
                    self.assign_task(staff)

    def tick_strat3(self):
        """
            Strategy 3:
            * staff 1 500hr find, staff 2 & 3 500hr fix ea.
            * Fix HE, LE, HH, LH.
        """
        self.sort_keys = lambda bug: (bug.time, bug.time)
        for staff in self.staff:
            if staff.id == 0: # Staff 0 always find
                if staff.task == None:
                    staff.task = FIND
            if staff.id == 1: # staff 2 always fix
                if type(staff.task) is not Bug:
                    self.assign_task(staff)
            if staff.id == 2: # Staff 2 always fix
                if type(staff.task) is not Bug:
                    self.assign_task(staff)
