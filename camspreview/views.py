from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import glob

def camspreviewindex(request):
    imagePath = '/run/user/1002/gvfs/smb-share:server=10.0.0.53,share=store_cams_picture/70143279/1/20210323/*.jpg'
    allImages = []
    for file in sorted(glob.glob(imagePath)):
        allImages.append(file)


    return render(request, 'camspreview.html',{'allImages':allImages})