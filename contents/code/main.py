from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
from subprocess import call
from subprocess import check_output
from os.path import basename

MAX_RESULTS = 5

class kruncmus(plasmascript.Runner):

    def init(self):
        # called upon creation to let us run any intialization
        # tell the user how to use this runner
        self.addSyntax(Plasma.RunnerSyntax("cmr :q:", "Display :q: in a messagebox"))

    def match(self, context):
        # called by krunner to let us add actions for the user
        if not context.isValid():
            return

        q = context.query()

        # look for our keyword 'msg'
        if not q.startsWith("cmr "):
             return

        # ignore less than 3 characters (in addition to the keyword)
        if q.length() < 7:
            return

        # strip the keyword and leading space
        q = q[3:]
        q = q.trimmed()

        # now create an action for the user, and send it to krunner
        call(["cmus-remote","-C","view sorted"])
        call(["cmus-remote","-C","live-filter " + q])

        output = ""
        output_next = ""

        m = Plasma.QueryMatch(self.runner)
        
        while True:

            output = basename(check_output(["cmus-remote","-C","echo {}"]))
            call(["cmus-remote","-C","win-down"])

            m.setText("Found: '%s'" % str(output))
            m.setType(Plasma.QueryMatch.ExactMatch)
            m.setIcon(KIcon("dialog-information"))
            m.setData(output)
            context.addMatch(output, m)
            
            output_next = basename(check_output(["cmus-remote","-C","echo {}"]))
            if output == output_next:
                break


    def run(self, context, match):
        # called by KRunner when the user selects our action,        
        # so lets keep our promise
        call(["cmus-remote","-C","live-filter " + match.data().toString()])
        call(["cmus-remote","-C","win-activate"])
        call(["cmus-remote","-C","live-filter"])


def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return kruncmus(parent)
