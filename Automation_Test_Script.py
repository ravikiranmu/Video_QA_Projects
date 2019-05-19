import requests
import os
import re

#Default URLS - Hostname/ipaddress need to be updated as per web server going to use for testing
mediaManifestURLPostCut = 'http://192.168.1.3/HLS_Segments_After_Cut/prog_index.m3u8'
subtitleManifestURLPostCut = 'http://192.168.1.3/HLS_Segments_After_Cut/english.m3u8'
mediaManifestURLPreCut = 'http://192.168.1.3/HLS_Segments_Before_Cut/prog_index.m3u8'
subtitleManifestURLPreCut = 'http://192.168.1.3/HLS_Segments_Before_Cut/english.m3u8'

def mediaManifestDownload(url):
    try:
        # Downloading media manifest file and story as file in current directory
        r = requests.get(url, allow_redirects=True)
        open('prog_index.m3u8', 'wb').write(r.content)
        
        #Checking segment entry on media manifest file
        mediaManifest = []                       # The list where we will store results.
        linenum = 0
        with open ('prog_index.m3u8', 'rt') as myfile:
            for line in myfile:
                linenum += 1
                #if line.lower().find(substr) != 0:    # if case-insensitive match,
                if line.lower() != 0:
                    mediaManifest.append(line.rstrip('\n\t'))
        return mediaManifest
    except Exception, e:
        print "Error observed while downloading media manifest file",e
        
def subtitleManifestDownload(url):
    try:
        # Downloading media manifest file and story as file in current directory
        r = requests.get(url, allow_redirects=True)
        open('subtitle.m3u8', 'wb').write(r.content)
        
        #Checking segment entry on media manifest file
        subtitleManifest = []                       # The list where we will store results.
        linenum = 0
        with open ('subtitle.m3u8', 'rt') as myfile:
            for line in myfile:
                linenum += 1
                #if line.lower().find(substr) != 0:    # if case-insensitive match,
                if line.lower() != 0:
                    subtitleManifest.append(line.rstrip('\n\t'))
        return subtitleManifest
    except Exception, e:
        print "Error observed while downloading media manifest file",e

def testDiscontinuityOnMediaManifest():
    try:        
        index = 0
        lineCount = 1
        discontinuityLineNo = 0
        segmentno = 0
        mediaManifest = mediaManifestDownload(mediaManifestURLPostCut)
        for text in mediaManifest:
            sub = "fileSequence{}.ts".format(index)
            if text == sub:
                index+= 1
                discontinuityLineNo = lineCount
                segmentno = index
            lineCount += 1
        
        print "Discontinuity Test result on Media Manifest file:"
        print "-------------------------------------------------"
        if discontinuityLineNo != 0:
            print "Discontinuity observed after fileSequence{}.ts segment".format(segmentno-1)
            print 'Media Manifest'
            print '--------------'
            print mediaManifest[discontinuityLineNo-1], '\n', mediaManifest[discontinuityLineNo], "\n", mediaManifest[discontinuityLineNo+1], "\n", mediaManifest[discontinuityLineNo+2], "\n", mediaManifest[discontinuityLineNo+3]
        else:
            print "Discontinuity not observed"
                
    except Exception, e:
        print e
        
def testDiscontinuityOnSubtitleManifest():
    try:        
        index = 0
        lineCount = 1
        discontinuityLineNo = 0
        segmentno = 0
        subtitleManifest = subtitleManifestDownload(subtitleManifestURLPostCut)
        for text in subtitleManifest:
            sub = "english{}.webvtt".format(index)
            if text == sub:
                index+= 1
                discontinuityLineNo = lineCount
                segmentno = index
            lineCount += 1
        
        print "\nDiscontinuity Test result on Subtitle Manifest file:"
        print "-------------------------------------------------"
        if discontinuityLineNo != 0:
            print "Discontinuity observed after english{}.ts segment".format(segmentno-1)
            print 'Subtitle Manifest'
            print '--------------'
            print subtitleManifest[discontinuityLineNo-1], '\n', subtitleManifest[discontinuityLineNo], "\n", subtitleManifest[discontinuityLineNo+1], "\n", subtitleManifest[discontinuityLineNo+2]
        else:
            print "Discontinuity not observed"
                
    except Exception, e:
        print e

def testtotalStreamDuration():
    mediaManifestPostCut = mediaManifestDownload(mediaManifestURLPostCut)
    subtitleManifestPostCut = subtitleManifestDownload(subtitleManifestURLPostCut)
    mediaManifestPreCut = mediaManifestDownload(mediaManifestURLPreCut)
    subtitleManifestPreCut = subtitleManifestDownload(subtitleManifestURLPreCut)
    
    # Media Manifest total duration post cut
    newlist1 = []
    avDurationPostCut = 0.0
    pattern = re.compile(r"(INF)+")
    for item in mediaManifestPostCut:
        if pattern.search(item) != None:
            newlist1.append(item)
    for item in newlist1:
        avDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    # Media Manifest total duration pre cut
    newlist2 = []
    avDurationPreCut = 0.0
    pattern = re.compile(r"(INF)+")
    for item in mediaManifestPreCut:
        if pattern.search(item) != None:
            newlist2.append(item)
    for item in newlist2:
        avDurationPreCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    differenceMediaDuraiton = (avDurationPreCut - avDurationPostCut)/60
    
    print "\nAV Total Duration Test Result"
    print "---------------------------"
    print "AV Duration(in mins):Pre Cut HLS Content", round(avDurationPreCut/60,0)
    print "AV Duration(in mins):Post Cut HLS Content", round(avDurationPostCut/60,0)
   
    if differenceMediaDuraiton <= 2.0:
        print "\nPass. Difference between AV duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton)
    else:
        print "\nFail. Difference between AV duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton), "\nExpected difference = 2mins"
    
    # Subtitle Manifest total duration post cut
    newlist3 = []
    subtitleDurationPostCut = 0.0
    pattern = re.compile(r"(INF)+")
    for item in subtitleManifestPostCut:
        if pattern.search(item) != None:
            newlist3.append(item)
    for item in newlist3:
        subtitleDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    # Subtitle Manifest total duration pre cut
    newlist4 = []
    subtitleDurationPreCut = 0.0
    pattern = re.compile(r"(INF)+")
    for item in subtitleManifestPreCut:
        if pattern.search(item) != None:
            newlist4.append(item)
    for item in newlist4:
        subtitleDurationPreCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    differenceSubtitleDuraiton = (subtitleDurationPostCut - subtitleDurationPreCut)/60
    
    print "\nSubtitle Total Duration Test Result"
    print "---------------------------"
    print "Subtitle Duration(in mins):Pre Cut HLS Content", round(subtitleDurationPreCut/60,0)
    print "Subtitle Duration(in mins):Post Cut HLS Content", round(subtitleDurationPostCut/60,0)
   
    if differenceMediaDuraiton <= 2.0:
        print "\nPass. Difference between Subtitle duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton)
    else:
        print "\nFail. Difference between Subtitle duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton), "\nExpected difference = 2mins"

def main():
    testDiscontinuityOnMediaManifest()
    testDiscontinuityOnSubtitleManifest()
    testtotalStreamDuration()
    os.remove("prog_index.m3u8")
    os.remove("subtitle.m3u8")
    
if __name__ == '__main__':
    main()