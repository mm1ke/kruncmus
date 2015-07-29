from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox

class MsgBoxRunner(plasmascript.Runner):

    def init(self):
        # called upon creation to let us run any intialization
        # tell the user how to use this runner
        self.addSyntax(Plasma.RunnerSyntax("msg :q:", "Display :q: in a messagebox"))

    def match(self, context):
        # called by krunner to let us add actions for the user
        if not context.isValid():
            return

        q = context.query()

        # look for our keyword 'msg'
        if not q.startsWith("msg "):
             return

        # ignore less than 3 characters (in addition to the keyword)
        if q.length() < 7:
            return

        # strip the keyword and leading space
        q = q[3:]
        q = q.trimmed()

        # now create an action for the user, and send it to krunner
        m = Plasma.QueryMatch(self.runner)
        m.setText("Message: '%s'" % q)
        m.setType(Plasma.QueryMatch.ExactMatch)
        m.setIcon(KIcon("dialog-information"))
        m.setData(q)
        context.addMatch(q, m)

    def run(self, context, match):
        # called by KRunner when the user selects our action,        
        # so lets keep our promise
        KMessageBox.messageBox(None, KMessageBox.Information, match.data().toString())


def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return MsgBoxRunner(parent)
