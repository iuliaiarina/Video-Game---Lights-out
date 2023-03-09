import os
import re
from subprocess import Popen, PIPE

PATH_TO_PROVER9 = "LADR-2009-11A/bin/mace4"
TMPFILE = "tmp.p9"
TEMPLATE = "allLights.in"

SOS_REGEX_STR = r"(formulas\(sos\)\.).*?(end_of_list\.)"
SOS_SUB_STR = r"\1\n{kb}\n\2"
SOS_REGEX = re.compile(SOS_REGEX_STR, re.MULTILINE|re.DOTALL)

GOALS_REGEX_STR = r"(formulas\(goals\)\.).*?(end_of_list\.)"
GOALS_SUB_STR = r"\1\n{goal}\n\2"
GOALS_REGEX = re.compile(GOALS_REGEX_STR, re.MULTILINE|re.DOTALL)

class Prover(object):
    def __init__(self):
        self.kb = set()
        os.chdir(os.path.dirname(__file__))
        with open(TEMPLATE) as f:
            self.template = f.read()
        self.template = SOS_REGEX.sub(SOS_SUB_STR, self.template)
        self.template = GOALS_REGEX.sub(GOALS_SUB_STR, self.template)
        self.wumpus = None


    def check_pit(self, x, y):
        return self.check("pit", x, y)

    def check(self, fact, x, y):
        rule1 = "chk_wumpus(%s,%s)." % (x,y)
        rule2 = "chk_pit(%s,%s)." % (x,y)
        self.kb.add(rule1)
        self.kb.add(rule2)
        result = self.prove("%s(%s,%s)." % (fact,x,y))
        self.kb.remove(rule1)
        self.kb.remove(rule2)
        return result

    def prove(self, goal):
        with open(TMPFILE,"w") as f:
            kb_str = "\n".join(self.kb)
            f.write(self.template.format(goal=goal, kb=kb_str))

        result = self.run_prover9()
        os.remove(TMPFILE)

        return re.search(r"THEOREM PROVED", result) is not None

    def run_prover9(self):
        cmd = [PATH_TO_PROVER9, '-f', TMPFILE]
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        return p.stdout.read()
