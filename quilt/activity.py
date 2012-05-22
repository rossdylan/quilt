import gtk 
from gettext import gettext as _ 
from sugar.activity import activity

class QuiltAcvity(activity.Activity): 
    """ Quilt Mesh Chat Client Activity """
    def __init__(self, handle, browser=None): 
        activity.Activity.__init__(self, handle)
        toolbox = activity.ActivityToolbox(self)
        toolbar = gtk.Toolbar()
        toolbox.add_toolbar(_('Quilt'), toolbar)
        toolbar.show()

        self.set_toolbox(toolbox)
        toolbox.show()
