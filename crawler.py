import urllib.error
import urllib.request
import urllib.response
import zipfile
import glob, os

i=0
baseURL='http://dl.opensubtitles.org/en/download/vrf-108d030f/sub/'
offset=6751059
response = urllib.request.urlopen(baseURL+str(offset))
print(response.geturl())
while i<50:
    offset+=1
    try:
        url=baseURL+str(offset)
        print(url)
        response = urllib.request.urlretrieve('http://dl.opensubtitles.org/en/download/vrf-108d030f/sub/'+str(offset),'archive.zip')
        print(response.__sizeof__())
        zip_ref = zipfile.ZipFile('archive.zip', 'r')
        zip_ref.extractall('subtitles')
        zip_ref.close()
        i+=1
    except urllib.error.HTTPError:
         print("Subtitle offset number "+str(offset)+" is invalid. Trying again...")

os.chdir('subtitles')
filelist = glob.glob("*.nfo")
for f in filelist:
    os.remove(f)
