from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
from subprocess import call
from subprocess import check_output
from os.path import basename

class kruncmus(plasmascript.Runner):

    def init(self):
        # called upon creation to let us run any intialization
        # tell the user how to use this runner
        self.addSyntax(Plasma.RunnerSyntax("cmr :q:", "Plays :q: in cmus"))

    def match(self, context):
        # called by krunner to let us add actions for the user
        if not context.isValid():
            return

        q = context.query()

        # look for our keyword 'cmr'
        if not q.startsWith("cmr "):
             return

        # ignore less than 3 characters (in addition to the keyword)
        if q.length() < 7:
            return

        # strip the keyword and leading space
        q = q[3:]
        q = q.trimmed()

        # now create an action for the user, and send it to krunner

        # goto libary, clear filter and search
        call(["cmus-remote","-C","view sorted"])
        call(["cmus-remote","-C","live-filter"])
        call(["cmus-remote","-C","live-filter " + q])

        output = ""

        m = Plasma.QueryMatch(self.runner)
        while True:

            output = basename(str(check_output(["cmus-remote","-C","echo {}"]))).rstrip('\\n\'').rstrip()
            if output == "":
                break

            m.setText("Play: '%s'" % output)
            m.setType(Plasma.QueryMatch.ExactMatch)
            m.setIcon(KIcon("media-playback-start"))
            m.setData(output)
            context.addMatch(output, m)

            call(["cmus-remote","-C","win-down"])
            # if we cant move down, names will be the same
            if output == basename(str(check_output(["cmus-remote","-C","echo {}"]))).rstrip('\\n\'').rstrip():
                break


    def run(self, context, match):

        # goto playlist and search for the track
        call(["cmus-remote","-C","view playlist"])
        call(["cmus-remote","-C","/" + match.data().toString()])
        result = basename(check_output(["cmus-remote","-C","echo {}"]))
        # if the track wasn't found cmus echo's the wrong track, thus simple check the names
        if result == match.data().toString():
            call(["cmus-remote","-C","win-activate"])
        # track not in playlist? add it!
        else:
            call(["cmus-remote","-C","view sorted"])
            call(["cmus-remote","-C","live-filter " + match.data().toString()])
            call(["cmus-remote","-C","win-add-p"])
            call(["cmus-remote","-C","live-filter"])
            call(["cmus-remote","-C","view playlist"])
            call(["cmus-remote","-C","/" + match.data().toString()])
            call(["cmus-remote","-C","win-activate"])



def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return kruncmus(parent)
