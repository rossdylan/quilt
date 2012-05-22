#!/usr/bin/env python

#Build OLPC Package
try: 
    from sugar.activity import bundlebuilder
    bundlebuilder.start()
except ImportError:
    try: 
        import os 
        os.system("find ./ | sed 's,^./,Quilt.activity/,g' > MANIFEST")
        os.chdir('..')
        os.system("zip -r Quilt.xo quilt.activity")
        os.system('mv Quilt.activity.xo ./Quilt.activity')
        os.chdir("quilt.activity")
        print "Done."
    except Exception as e:
        print e
