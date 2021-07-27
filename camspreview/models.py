from django.db import models

# Create your models here.
class Image(models.Model):
    
    def get_image_path(self):
        for root, dirs, files in os.walk('/run/user/1002/gvfs/smb-share:server=10.0.0.53,share=store_cams_picture/70143279/1/20210323'):
            #debug information, just to get an idea how walk works.
            #currently we are traversing over all files with any extension
            print("Current directory", root)
            print("Sub directories", dirs)
            print("Files", files)

            for file in files:
                if file.startswith(self.title):
                    #now we have found the desired file.
                    #value of file: "myimagetitle.jpg" <-- no path info
                    #value of root: "/home/yourhome/gallery/static/images/myalbum"
                    #we want to use this information to create a url based on our static path, so we need only the path sections past "static"
                    #we can achieve this like so (just one way)
                    mypath = os.sep.join(os.path.join(root, file).split(os.sep)[4:])
                    print(mypath)
                    #yields: /images/myalbum/myimagetitle.jpg

                    return mypath