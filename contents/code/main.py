from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
from subprocess import call
from subprocess import check_output
from os.path import basename
import glob

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

        # look for our keyword's
        #   cmp     cmus play - play track (also adds to playlist if not there)
        #   cml     cmus playlist - load playlist and play
        #   cmq     cmus queue - add track to queue
        #   cmt     cmus toggle - toggle settings
        if not (q.startsWith("cmp ") or q.startsWith("cml") or q.startsWith("cmq ") or q.startsWith("cmt")):
            return

        m = Plasma.QueryMatch(self.runner)
        
        # ignore less than 3 characters (in addition to the keyword)
        if q.startsWith("cmt"):
            for t in ["continue","repeat","repeat_current","shuffle"]:
                m.setText("Toggle: '%s'" % t)
                m.setType(Plasma.QueryMatch.ExactMatch)
                m.setIcon(KIcon("media-playback-start"))
                m.setData(t)
                context.addMatch(t, m)

        else:
            # strip the keyword and leading space
            keyword = q[3:]
            keyword = keyword.trimmed()

            if q.startsWith("cml"):
                print("asdf")

                PLAYLIST_DIR="/home/michael/Downloads/music/playlists/"
                for f in glob.glob(PLAYLIST_DIR + str(keyword) + "*"):
                    m.setText("Play: '%s'" % basename(str(f)))
                    m.setType(Plasma.QueryMatch.ExactMatch)
                    m.setIcon(KIcon("media-playback-start"))
                    m.setData(f)
                    context.addMatch(f, m)

            else:
                if q.length() < 7:
                    return

                # goto libary, clear filter and search
                call(["cmus-remote","-C","view sorted"])
                call(["cmus-remote","-C","live-filter"])
                call(["cmus-remote","-C","live-filter " + keyword])
                
                output = ""

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
        
        q = context.query()

        if q.startsWith("cmp "):
            # goto playlist and search for the track
            call(["cmus-remote","-C","view playlist"])
            call(["cmus-remote","-C","/" + match.data().toString()])
            result = basename(str(check_output(["cmus-remote","-C","echo {}"]))).rstrip('\\n\'').rstrip()
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

        elif q.startsWith("cmq "):
            call(["cmus-remote","-C","view sorted"])
            call(["cmus-remote","-C","live-filter " + match.data().toString()])
            call(["cmus-remote","-C","win-add-q"])

        elif q.startsWith("cml"):
            call(["cmus-remote","-C","view playlist"])
            call(["cmus-remote","-C","load " + match.data().toString()])
            call(["cmus-remote","-C","win-activate"])

        elif q.startsWith("cmt "):
            print("ok")




def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return kruncmus(parent)
