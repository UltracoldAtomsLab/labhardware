#!/usr/bin/env python
import sys

#import matplotlib 
#matplotlib.use('GTK') 
#from matplotlib.figure import Figure 
#from matplotlib.axes import Subplot 
#from matplotlib.backends.backend_gtk import FigureCanvasGTK, NavigationToolbar 
#from matplotlib.numerix import arange, sin, pi 

import ConfigParser
import os

try: 
    import pygtk 
    pygtk.require("2.0") 
except: 
    pass 
try: 
    import gtk
    import gtk.gdk
    import gobject
    import gtk.glade 
except: 
    sys.exit(1)

import transstage

def catch_button(window, event, label):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        print event.state
        mod = gtk.accelerator_get_label(keyval,event.state)
        label.set_markup('<span size="xx-large">%s\n%d</span>'% (mod, keyval))
 
 
class appGui: 
    def __init__(self, cont):
        self.cont = cont
        self.moveenabled = False
        dirname = os.path.dirname(sys.argv[0])
        gladefile = dirname + "/experiment02.glade"
        self.windowname = "window1" 
        self.wTree = gtk.glade.XML(gladefile, self.windowname)
        dic = {"on_mainWindow_destroy" : gtk.main_quit}
        self.wTree.signal_autoconnect(dic)
        self.window = self.wTree.get_widget(self.windowname)
        self.window.show_all()
        dic = {"on_window1_destroy" : gtk.main_quit, 
              }
        self.wTree.signal_autoconnect(dic)
        self.poslabel = self.wTree.get_widget("PositionLabel")
        self.window.connect('key-press-event', self.windowkey)

        self.stepbuttons = []
        for i in range(5):
            self.stepbuttons.append(self.wTree.get_widget("stepbutton%d"%(i+1)))
        self.stepbuttons[0].set_active(True)

        # Step sizes of 1um, 1mm, 10mm
        self.stepsizes = [10000, 1000, 100, 10, 1]
        # From measurement
        self.scale = 6487485 / 200000.0 * 1.875

        self.pollposition(self.poslabel)
        gobject.timeout_add(1000, self.pollposition, self.poslabel)
        self.moveenabled = True

        # Set move direction
        self.moveposbtn = self.wTree.get_widget("MovePosBtn")

        # Alternative position
        self.altpos = None

        self.homesetbtn = self.wTree.get_widget("button1")
        self.homesetbtn.connect('clicked', self.homeset)
        self.gohomebtn = self.wTree.get_widget("button2")
        self.gohomebtn.connect('clicked', self.gohome)

        self.setaltposbtn = self.wTree.get_widget("SetAltPosBtn")
        self.setaltposbtn.connect('clicked', self.setaltpos)
        self.goaltposbtn = self.wTree.get_widget("GoToAltPosBtn")
        self.goaltposbtn.connect('clicked', self.goaltpos)
        self.altposlabel = self.wTree.get_widget("AltPosLabel")
        self.altposlabel.set_text("Not set")

    def countfum(self, um):
        return int(self.scale * um)

    def umfcount(self, count):
        return count / self.scale
        
    def windowkey(self, widget, event):
        direction = ["-", '+']
        if not self.moveposbtn.get_active():
            direction.reverse()
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        if (name == "Left"):
            self.movestage(direction[0])
        elif (name == "Right"):
            self.movestage(direction[1])

    def getstepsize(self):
        i = 0
        for button in self.stepbuttons:
            if not button.get_active():
                i = i + 1
            else:
                break
        return self.countfum(self.stepsizes[i])

    def movestage(self, direction):
        distance = self.getstepsize()
        if (direction == "-"):
            distance *= -1
        if self.moveenabled :
            cont.command("MR%d"%(distance))

    def pollposition(self, label):
        pos = self.cont.getposition()
        label.set_text("%d count\n%.4f mm"%(pos, \
                       self.umfcount(pos)/1000))
        return True

    def homeset(self, widget):
        # Refresh the alternative position
        current = self.cont.getposition()
        self.setaltpos(self, position=(self.altpos - current))
        # Set home
        cont.command("DH")

    def gohome(self, widget):
        cont.command("MA0")

    def setaltpos(self, widget=None, position=None):
        if not position:
            self.altpos = self.cont.getposition()
        else:
            self.altpos = position
        self.altposlabel.set_text("%.4f mm" \
                                  %(self.umfcount(self.altpos)/1000.0))

    def goaltpos(self, widget):
        if self.altpos:
            self.cont.command("MA%d" %(self.altpos))

if __name__ == "__main__":
    dirname = os.path.dirname(sys.argv[0])
    cont = transstage.MotorControl('/dev/ttyUSB0')

    splash = gtk.Window()
    splashimg = gtk.Image()
    splashimg.set_from_file('splash.svg')
    splash.add(splashimg)
    splash.show_all()
    # Needed to display splash during the setup sequence
    while gtk.events_pending():
        gtk.main_iteration()
    try:
        config = ConfigParser.RawConfigParser()
        config.read(dirname+'/stage.conf')
        section = 'PID'
        for opt in config.options(section):
            print "Set %s -> %s" %(opt, config.get(section, opt))
            cont.setparam(opt, int(config.get(section, opt)))
    except:
        print "Error when parsing/applying settings. Continue anyway."
        pass
    splash.hide()
    app = appGui(cont)
    gtk.main()
