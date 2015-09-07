from PyKDE4 import plasmascript
from PyKDE4.plasma import Plasma
from PyKDE4.kdeui import KIcon, KMessageBox
from subprocess import call
from subprocess import check_output
from subprocess import Popen
from subprocess import PIPE
from os.path import basename
import glob
import re

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
        #   cmc     cmus control - toggle settings + pause/play/next/previous
        if not (q.startsWith("cmp ") or q.startsWith("cml") or q.startsWith("cmq ") or q.startsWith("cmc")):
            return

        # check if cmus is running
        s = Popen(["ps","axw"],stdout=PIPE)
        for x in s.stdout:
            if re.search("cmus",x):
                cmus_running=True

        if not cmus_running:
            return


        m = Plasma.QueryMatch(self.runner)
        m.setIcon(KIcon("media-playback-start"))
        m.setType(Plasma.QueryMatch.ExactMatch)

        # ignore less than 3 characters (in addition to the keyword)
        if q.startsWith("cmc"):
            # get cmus-remote -Q output and split them
            status=str(check_output(["cmus-remote","-Q"])).rstrip('\\n\'').replace('b\'','').replace('\\n','\n').split('\n')
            settings={"status":'%s' % status[0][7:],
                    "file":'%s' % basename(status[1][5:]),
                    "continue":'%s' % status[5][13:],
                    "repeat":'%s' % status[11][11:],
                    "repeat_current":'%s' % status[12][19:],
                    "shuffle":'%s' % status[13][12:]}

            m.setText("Toggle %s: %s" % (settings['status'],settings['file']))
            m.setData("player-pause")
            context.addMatch(settings['file'], m)


            m.setText("Play next track")
            m.setData("player-next")
            context.addMatch("next", m)

            m.setText("Play previous track")
            m.setData("player-prev")
            context.addMatch("prev", m)


            for t in ["continue","repeat","repeat_current","shuffle"]:
                m.setText("Toggle %s (%s)" % (t.replace('_',' '),settings[t]))
                m.setData("toggle " + t)
                context.addMatch(t, m)

        else:
            # strip the keyword and leading space
            # but don't wait until user entered something
            keyword = q[3:]
            keyword = keyword.trimmed()

            if q.startsWith("cml"):
                PLAYLIST_DIR="/home/michael/Downloads/music/playlists/"
                for f in glob.glob(PLAYLIST_DIR + str(keyword) + "*"):
                    m.setText("Play: '%s'" % basename(str(f)))
                    m.setData(f)
                    context.addMatch(f, m)

            else:
                if q.length() < 7:
                    return

                # goto libary, clear filter and search
                call(["cmus-remote","-C","view sorted"])
                call(["cmus-remote","-C","live-filter " + keyword])

                output = ""
                counter = 0

                while True:
                    counter += 1

                    output = basename(str(check_output(["cmus-remote","-C","echo {}"]))).rstrip('\\n\'').rstrip()
                    if output == "":
                        break

                    m.setText("Play: '%s'" % output)
                    m.setData(output)
                    context.addMatch(output, m)

                    # dont show more than 10 results
                    if counter > 10:
                        break

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

        elif q.startsWith("cmc"):
            call(["cmus-remote","-C"," " + match.data().toString()])


def CreateRunner(parent):
    # called by krunner, must simply return an instance of the runner object
    return kruncmus(parent)
