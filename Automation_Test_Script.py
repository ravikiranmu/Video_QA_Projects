import requests
import os
import re

#Default URLS - Hostname/ipaddress need to be updated as per web server going to use for testing
mediaManifestURLPostCut = 'http://192.168.3.100/HLS_Segments_After_Cut/prog_index.m3u8'
subtitleManifestURLPostCut = 'http://192.168.3.100/HLS_Segments_After_Cut/english.m3u8'
mediaManifestURLPreCut = 'http://192.168.3.100/HLS_Segments_Before_Cut/prog_index.m3u8'
subtitleManifestURLPreCut = 'http://192.168.3.100/HLS_Segments_Before_Cut/english.m3u8'

def mediaManifestDownload(url):
    """
    This function will download the media manifest file from web-server
    """
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
    """
    This function will download the subtitle manifest file from web-server
    """
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
    """
    This function will test the presences of #EXT-X-DISCONTINUITY tag on media manifest file
    """
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
            if mediaManifest[discontinuityLineNo] == '#EXT-X-DISCONTINUITY':
                print "Discontinuity observed after fileSequence{}.ts segment".format(segmentno-1)
            else:
                print "Discontinuity tag is not present and the result is Fail"
            print 'Media Manifest'
            print '--------------'
            print mediaManifest[discontinuityLineNo-1], '\n', mediaManifest[discontinuityLineNo], "\n", mediaManifest[discontinuityLineNo+1], "\n", mediaManifest[discontinuityLineNo+2], "\n", mediaManifest[discontinuityLineNo+3]
        else:
            print "Discontinuity not observed"
                
    except Exception, e:
        print e
        
def testDiscontinuityOnSubtitleManifest():
    """
    This function will test the presences of #EXT-X-DISCONTINUITY tag on subtitle manifest file
    """
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
            if subtitleManifest[discontinuityLineNo] == '#EXT-X-DISCONTINUITY':
                print "Discontinuity observed after english{}.ts segment".format(segmentno-1)
            else:
                print "Discontinuity tag is not present and the result is Fail"
            
            print 'Subtitle Manifest'
            print '--------------'
            print subtitleManifest[discontinuityLineNo-1], '\n', subtitleManifest[discontinuityLineNo], "\n", subtitleManifest[discontinuityLineNo+1], "\n", subtitleManifest[discontinuityLineNo+2]
        else:
            print "Discontinuity not observed"
                
    except Exception, e:
        print e

def testtotalStreamDuration():
    """
    This function will test total duration of the VOD content after the cut
    """
    mediaManifestPostCut = mediaManifestDownload(mediaManifestURLPostCut)
    subtitleManifestPostCut = subtitleManifestDownload(subtitleManifestURLPostCut)
    mediaManifestPreCut = mediaManifestDownload(mediaManifestURLPreCut)
    subtitleManifestPreCut = subtitleManifestDownload(subtitleManifestURLPreCut)
    pattern = re.compile(r"(INF)+")
    
    # Media Manifest total duration post cut
    newlist1 = []
    avDurationPostCut = 0.0
    for item in mediaManifestPostCut:
        if pattern.search(item) != None:
            newlist1.append(item)
    for item in newlist1:
        avDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    # Media Manifest total duration pre cut
    newlist2 = []
    avDurationPreCut = 0.0
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
   
    if str(round(differenceMediaDuraiton,0)) >= str(2.0):
        print "\nPass. Difference between AV duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton)
    else:
        print "\nFail. Difference between AV duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton), "\nExpected difference = 2mins"
    
    # Subtitle Manifest total duration post cut
    newlist3 = []
    subtitleDurationPostCut = 0.0
    for item in subtitleManifestPostCut:
        if pattern.search(item) != None:
            newlist3.append(item)
    for item in newlist3:
        subtitleDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    # Subtitle Manifest total duration pre cut
    newlist4 = []
    subtitleDurationPreCut = 0.0
    for item in subtitleManifestPreCut:
        if pattern.search(item) != None:
            newlist4.append(item)
    for item in newlist4:
        subtitleDurationPreCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    differenceSubtitleDuraiton = (subtitleDurationPreCut - subtitleDurationPostCut)/60
    
    print "\nSubtitle Total Duration Test Result"
    print "---------------------------"
    print "Subtitle Duration(in mins):Pre Cut HLS Content", round(subtitleDurationPreCut/60,0)
    print "Subtitle Duration(in mins):Post Cut HLS Content", round(subtitleDurationPostCut/60,0)
   
    if str(round(differenceSubtitleDuraiton)) >= str(2.0):
        print "\nPass. Difference between Subtitle duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton)
    else:
        print "\nFail. Difference between Subtitle duration(in mins) of pre-cut content and post cut content is", round(differenceMediaDuraiton), "\nExpected difference = 2mins"

def testChopOutDuration():
    """
    This function will test the chop duration on both media manifest file and subtitle manifest file to determine the video sync with subtitle
    """
    mediaManifestPostCut = mediaManifestDownload(mediaManifestURLPostCut)
    subtitleManifestPostCut = subtitleManifestDownload(subtitleManifestURLPostCut)
    mediaManifestPreCut = mediaManifestDownload(mediaManifestURLPreCut)
    subtitleManifestPreCut = subtitleManifestDownload(subtitleManifestURLPreCut)
    pattern = re.compile(r"(INF)+")
    
    #Identify the cut happening at media manifest file
    last1 = len(mediaManifestPostCut) - 1
    result1 = [[]]
    for i, v in enumerate(mediaManifestPostCut):
        if v == "#EXT-X-DISCONTINUITY":
            result1[-1].append("#EXT-X-DISCONTINUITY")
            if i != last1:
                result1.append([])
        else:
            result1[-1].append(v)
    
    beforeCutAV = []
    beforeCutDurationAV = 0.0
    for item in result1[0]:
        if pattern.search(item) != None:
            beforeCutAV.append(item)
    for item in beforeCutAV:
        beforeCutDurationAV += float((item.split(':',1)[1]).split(',',1)[0])

    afterCutAV = []
    afterCutDurationAV = 0.0
    for item in result1[1]:
        if pattern.search(item) != None:
            afterCutAV.append(item)
    for item in afterCutAV:
        afterCutDurationAV += float((item.split(':',1)[1]).split(',',1)[0])

    newlist1 = []
    avDurationPostCut = 0.0
    for item in mediaManifestPostCut:
        if pattern.search(item) != None:
            newlist1.append(item)
    for item in newlist1:
        avDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
            
    # Media Manifest total duration pre cut
    newlist2 = []
    avDurationPreCut = 0.0
    for item in mediaManifestPreCut:
        if pattern.search(item) != None:
            newlist2.append(item)
    for item in newlist2:
        avDurationPreCut += float((item.split(':',1)[1]).split(',',1)[0])
            
    differenceMediaDuraiton = (avDurationPreCut - avDurationPostCut)/60
    
    print "\nChop Duration test result for AV:"
    print "----------------------------------------"
    
    if str(avDurationPreCut/60) == str((beforeCutDurationAV/60)+(afterCutDurationAV/60)+differenceMediaDuraiton):
        print "AV cut happened from {0} mins and resumed at {1}".format((beforeCutDurationAV/60),((beforeCutDurationAV/60)+differenceMediaDuraiton))
    
    #Identify the cut happening at subtitle manifest file    
    last2 = len(subtitleManifestPostCut) - 1
    result2 = [[]]
    for i, v in enumerate(subtitleManifestPostCut):
        if v == "#EXT-X-DISCONTINUITY":
            result2[-1].append("#EXT-X-DISCONTINUITY")
            if i != last2:
                result2.append([])
        else:
            result2[-1].append(v)
    
    beforeCutSubtitle = []
    beforeCutDurationSubtitle = 0.0
    for item in result2[0]:
        if pattern.search(item) != None:
            beforeCutSubtitle.append(item)
    for item in beforeCutSubtitle:
        beforeCutDurationSubtitle += float((item.split(':',1)[1]).split(',',1)[0])

    afterCutSubtitle = []
    afterCutDurationSubtitle = 0.0
    for item in result2[1]:
        if pattern.search(item) != None:
            afterCutSubtitle.append(item)
    for item in afterCutSubtitle:
        afterCutDurationSubtitle += float((item.split(':',1)[1]).split(',',1)[0])

    # Subtitle Manifest total duration post cut
    newlist3 = []
    subtitleDurationPostCut = 0.0
    for item in subtitleManifestPostCut:
        if pattern.search(item) != None:
            newlist3.append(item)
    for item in newlist3:
        subtitleDurationPostCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    # Subtitle Manifest total duration pre cut
    newlist4 = []
    subtitleDurationPreCut = 0.0
    for item in subtitleManifestPreCut:
        if pattern.search(item) != None:
            newlist4.append(item)
    for item in newlist4:
        subtitleDurationPreCut += float((item.split(':',1)[1]).split(',',1)[0])
        
    differenceSubtitleDuraiton = (subtitleDurationPreCut - subtitleDurationPostCut)/60
    
    print "\nChop Duration test result for Subtitle:"
    print "----------------------------------------"
    
    if str(subtitleDurationPreCut/60) == str((beforeCutDurationSubtitle/60)+(afterCutDurationSubtitle/60)+differenceSubtitleDuraiton):
        print "Subtitle cut happened from {0} mins and resumed at {1}".format((beforeCutDurationSubtitle/60),((beforeCutDurationSubtitle/60)+differenceSubtitleDuraiton))

    if ((int(beforeCutDurationSubtitle/60) == int(beforeCutDurationAV/60)) and int(((beforeCutDurationSubtitle/60)+differenceSubtitleDuraiton)) == int(((beforeCutDurationAV/60)+differenceMediaDuraiton))):
        print "\nAV is synced with Subtitle"
    else:
        print "\n AV is not synced with Subtitle"

def main():
    testDiscontinuityOnMediaManifest()
    testDiscontinuityOnSubtitleManifest()
    testtotalStreamDuration()
    testChopOutDuration()
    os.remove("prog_index.m3u8")
    os.remove("subtitle.m3u8")
    
if __name__ == '__main__':
    main()