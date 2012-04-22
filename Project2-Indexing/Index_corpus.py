'''
Created on May 28, 2011

@author: Naveen
'''
# 1. Create a pickle of the format.
#       - (docIntId, term , [pos1,posn2,..]

import re,os,time

def makeStemHashPickle():
    file = open(STEM_FILE,'r')
    varStemHash = {}
    file.readline()
    for line in file:
        root,vars = line.split("|")
        for var in vars.split():
            varStemHash[var.strip()] = root.strip()
    file.close()
    print "DEBUG: [makeStemHashPickle] Length of hash:",len(varStemHash)
    return varStemHash
        
def doPickling(option,pickleFile,obj=None):
    varRootHash = {} 
    from pickle import Pickler  
    if os.path.isfile(pickleFile):
        os.remove(pickleFile)
        print "DEBUG:[Pickling] Removing existing pickleFile: ",pickleFile
    f = open(pickleFile,"w")
    if option == "STEM_TEXT":
        print "DEBUG:[Pickling] Pickling variation and roots..."
        varRootHash = makeStemHashPickle() 
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stemmedQTList
        p = Pickler(f)
        p.dump(varRootHash)
        f.close()
    elif option == "TERM_CTFMAP" :
        print "DEBUG:[Pickling] Pickling Term CTF..."
        termCtfHash = obj 
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stemmedQTList
        p = Pickler(f)
        p.dump(termCtfHash)
        f.close()
    elif option == "STOPLIST" :
        print "DEBUG:[Pickling] Pickling stop list..."
        stoplstfile = open(STOPLIST_FILE,'r')
        stopmap = {}
        for word in stoplstfile:
            word = word.strip()
            stopmap[word]=" "
        stoplstfile.close()
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stopmap
        p = Pickler(f)
        p.dump(stopmap)
        f.close()
    elif option == "CATALOG" :
        print "DEBUG:[Pickling] Pickling CATALOG..."
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stemmedQTList
        p = Pickler(f)
        p.dump(makecataloghash())
        f.close()
 
def doUnPickling(option,pickleFile):
    varRootHash = {}
    from pickle import Unpickler
    if not os.path.isfile(pickleFile):
        print "DEBUG:[doUnPickling] PickleFile does not exist."
        if option == "TERM_CTFMAP":
            print "****ERROR Unpickling****"; exit(1)
        doPickling(option,pickleFile)
    f = open(pickleFile,"r")
    if option == "STEM_TEXT":
        up = Unpickler(f)
        varRootHash = up.load()
        f.close()
#        print "DEBUG:[doUnPickling] Unpickled "+option+": "#,unpkldData
        return varRootHash  
    elif option == "TERM_CTFMAP" :
        print "DEBUG:[doUnpickling] UnPickling Term CTF..."
        up = Unpickler(f)
        termCtfHash = up.load()
        f.close()
        return termCtfHash
    elif option == "STOPLIST" :
        print "DEBUG:[doUnpickling] UnPickling stoplist..."
        up = Unpickler(f)
        stoplst = up.load()
        f.close()
        return stoplst
    elif option == "CATALOG" :
        print "DEBUG:[doUnpickling] UnPickling Catalog.."
        up = Unpickler(f)
        termSeekHash = up.load()
        f.close()
        return termSeekHash

    
contr = {"i'd":"i had", "you'd":"you had", "they,d":"they had", "he'd":"he had", "here's":"here is", \
         "isn't":"is not", "couldn't":"could not", "I'll":"i will", "you'll":"you will", "they'll":"they will",\
         "he'll":"he will", "there's":"there is", "aren't":"are not","shouldn't":"should not", \
         "i'm":"i am", "you're":"you are", "they're":"they are", "he's":"he is", "where's":"where is", \
         "don't":"do not", "wouldn't":"would not", "i've":"i have", "you've":"you have", "they've":"they have", "she'd":"she had", \
         "what's":"what is", "doesn't":"does not", "won't":"would not", "it'll":"it will", "we'd":"we had", "we're":"we are", \
         "she'll":"she will", "who'll":"who will", "didn't":"did not", "weren't":"were not", "it's":"it is", "we'll":"we will",\
         "we've":"we have","she's":"she is", "who's":"who is", "can't":"can not", "let's":"let us"}

def removeContractions(words):
#    print words
#    if len(words)== 0: return []
    newlst = []; keys = contr.keys()
    for word in words:
        word = word.lower()
        if word in keys:
            exp = contr[word];
            exp = exp.split()
            newlst.append(exp[0]);
            newlst.append(exp[1])
        else:
            word = re.sub("'s","s",word)
            word = re.sub("'","",word) 
#            print word
            if str.isalnum(word):
                newlst.append(word)
    return newlst
         

def doParse(fullText):
    docData = []
#    pat = "<DOCNO>\s*(.*?)\s*</DOCNO>.*?<\s*TEXT\s*>\n\s*(.*?)\n</\s*TEXT\s*>"
    docpat = "<\s*DOC\s*>\s*(.*?)\s*</\s*DOC\s*>"
    docidpat= "<\s*DOCNO\s*>\s*(.*?)\s*</\s*DOCNO\s*>"
    textpat = "<\s*TEXT\s*>\s*(.*?)</\s*TEXT\s*>"
    headpat = "<\s*HEAD\s*>\s*(.*?)</\s*HEAD\s*>"
    # Remove all entities
    fullText = re.sub("&amp;"," ",fullText)
    fullText = re.sub("&lbsp;"," ",fullText)
    fullText = re.sub("&rsqb;"," ",fullText)
    fullText = re.sub("&plus;"," ",fullText)
    fullText = re.sub("&equals;"," ",fullText)
    fullText = re.sub(r"\n"," ",fullText)
    fullText = re.sub("[*+=:&;~|)(\[\]{}\"]"," ",fullText)
    fullText = re.sub("[$?!#%^`]","",fullText)
#    fullText = fullText.lower()
    
    docDataRaw = re.findall(docpat, fullText,re.DOTALL);
    for doc in docDataRaw:
        docidArr = re.findall(docidpat, doc , re.DOTALL)
        docid = docidArr[0]
        def remSpecialChars(text):
            text = text.lower()
            text = re.sub("[-_@]"," ",text)
            text = re.sub(r"\\"," ",text)
            text = re.sub(", "," ",text)
            text = re.sub("\. "," ",text)
            text = re.sub("\.,"," ",text)
            ## instead of the below ones the contractiosn are removed
            text = re.sub("(')+$","",text) #Order of removal matters
            text = re.sub("[.,]","",text)
            text = re.sub("''","",text)
#            print "doParse:",text
            return text
        
        textArr = re.findall(textpat,doc,re.DOTALL)
        headArr = re.findall(headpat,doc,re.DOTALL)
        if not len(textArr) == 0:
            textArr = map(remSpecialChars,textArr)
        if not len(headArr) == 0:
            headArr = map(remSpecialChars,headArr)
        text =" ".join(headArr)+" "+" ".join(textArr)
#        print "Before doclean stem"
        text = doCleanStem(text)
#        print docid,len(text)

#        print "%s %s"%(docid,str(len(text)))
        docData.append((docid,text))
#    exit(1)   
    return docData



def doIndex():
    stoplst = doUnPickling("STOPLIST", STOPPICKLE_PATH)
    print "PROFILE:[DO Index] TIMER STARTS"
    et = time.time(); ct = time.clock();
    # DS: uniq_term_hash
    #     -> {term : (docid,[positions])}
    uniq_term_hash = {}; docLenMap = {}; docIntExtMap = {}; ctfMap = {}; 
    docIntId = 1; sumDoclen = 0;
    outputFile = ""
    for fname in os.listdir(CORPUS_DIR):
        outputFile = INT_CORPUS_DIR+"/"+fname+"_out"
        txtFile = open(CORPUS_DIR+"/"+fname,'r')
        fullText = txtFile.read();txtFile.close()
#        print "PROFILE:[applying regex remove] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
        docData = doParse(fullText)
#        exit(1)
        print "PROFILE:[Parsing document] TIMER STARTS"
        e0 = time.time(); c0 = time.clock();
        for docExtId,text in docData:
            docIntExtMap[docIntId] = docExtId
            docExtId = docIntId
            if len(text)>0: stemdText = text
            else:  stemdText = []
            i = 1;doclen = 0
            for word in stemdText:
                if stoplst.has_key(word):
                    i += 1 # i maintains the positions
                    continue
                if uniq_term_hash.has_key(word):
                    docIdMap = uniq_term_hash[word]
                    if docIdMap.has_key(docExtId):
                        poslst = docIdMap[docExtId]
                        poslst.append(i)
                        uniq_term_hash[word][docExtId] = poslst
                    else:
                        uniq_term_hash[word][docExtId] = [i]
                else:
                    newmap = {}
                    newmap[docExtId]=[i]
                    uniq_term_hash[word] = newmap
                i += 1
                doclen += 1 # increment only if it is not a stopword
            docLenMap[docExtId]= doclen
            docIntId += 1
            print "%s %s:%s doclen:%s"%(fname,str(docExtId),docIntExtMap[docExtId],str(doclen))
        print "PROFILE:[Parsing Document] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
        print "PROFILE:[File writing]"+fname+" TIMER STARTS"
        e0 = time.time(); c0 = time.clock();
        ofile = open(outputFile,'a')
#        fileOffset = ofile.tell()
#        termSeekMap = {}
        for term in sorted(uniq_term_hash.keys()):
            docIdMap = uniq_term_hash[term]
            outString = ""
            for docId in sorted(docIdMap.keys()):
                poslst = docIdMap[docId]
                tf = len(poslst)
                # create a list of file seek positions in 
                if ctfMap.has_key(term):
                    ctf = ctfMap[term]
                    ctfMap[term] = (ctf + tf)
                else:
                    ctfMap[term] = tf
                outString += " "+str(docId)+":"+str(docLenMap[docId])+":"+str(tf)+":"+",".join(map(str,poslst))
            ofile.write("%s %s\n" %(term,outString))
        ofile.close()
        print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
        dfile = open(docLenFile,'a')
        for docid in sorted(docLenMap.keys()):
            sumDoclen += docLenMap[docid];
            dfile.write("%s %s %s\n" %(str(docid),docIntExtMap[docid],str(docLenMap[docid])))
        dfile.close()
        docLenMap = {}
        uniq_term_hash = {}
        print "****** ----"+fname+"-------**********"
    print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
#    doPickling("TERM_CTFMAP", ctfTermMapFile, ctfMap)
    
    ctfhandle = open(ctfTermMapFileCheck,"w")
    ctfMaptpls = sorted(ctfMap.items(),key=lambda atpl:atpl[1],reverse=True)
    x = len(ctfMaptpls)
#    print "ctfMaptpls:::Len=",
#    print "len%200",x%1500
    ctfhandle.write("SumDocLen: %s"%(str(sumDoclen)))
    for term,ctf in ctfMaptpls:
        ctfhandle.write("%s %s\n"%(term,ctf))
    ctfhandle.close()
#    doPickling("FILE_SEEK", fileSeekMapPath, fileSeekMap)
#    fileSeekMapPathCheck = "E:/NEU/Ir/Project2/ap/ap/out/fileSeekMap.txt"
#    fhandle = open(fileSeekMapPathCheck,'w')
#    for filename in sorted(fileSeekMap.keys()):
#        fhandle.write("%s %s\n"%(filename,str(fileSeekMap[filename])))
#    fhandle.close()
    

def makeCatalog():
    print "PROFILE:[Total Time] TIMER STARTS"
    et = time.time(); ct = time.clock();
    indexhandle = open(indexFilePath,'a')
    cataloghandle = open(catalogFilePath,'a')
    termhashMaster = ["a","b","c",["d","e"],"f",["g","h","i"],["j","k","l"],"m","n","o","p","q","r","s","t","u","v",["w","x","y","z"],["0","1","2","3"],["4","5","6"],["7","8","9"]]
    for termstart in termhashMaster:
        if not isinstance(termstart,list):
            termstart = [termstart]
        termhash = {}
#       print "PROFILE:[ "+fname+" ] TIMER STARTS"
        e0 = time.time(); c0 = time.clock();
        for fname in os.listdir(INT_CORPUS_DIR):
            aFile = INT_CORPUS_DIR+"/"+fname
            docIndexHandle = open(aFile,'r')

            for line in docIndexHandle:
                term,postlst = str.split(line," ",1)
                term = term.strip();postlst = postlst.strip()
                if termhash.has_key(term):
                    plstInMap = termhash[term]
                    termhash[term]= plstInMap +" "+ postlst
                    plstInMap = ""
                elif term[0] in termstart:
                        termhash[term]=postlst
                        postlst = ""
                else: continue;
#            print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
#        indexhandle = open(indexFilePath,'a')
#        cataloghandle = open(catalogFilePath,'a')
#        print "PROFILE:[ Writing "+termstart+str(len(termhash))+" ] TIMER STARTS"
#        e0 = time.time(); c0 = time.clock();
        for term in termhash.keys():
            idxoffset = indexhandle.tell();
            indexhandle.seek(idxoffset)
            indexhandle.write("%s  %s\n"%(term,termhash[term]))
            cataloghandle.write("%s %s\n"%(term,idxoffset))
#        indexhandle.close();cataloghandle.close();
        termhash = {}
        print "**-->"+" ".join(termstart)+"<--***"
        print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    indexhandle.close();cataloghandle.close();
#        exit(1)
    print "PROFILE:[Total ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
    
zipIndexFilePath = "E:/NEU/Ir/Project2/ap/final/ZipIndexFile.txt"
zipCatalogFilePath = "E:/NEU/Ir/Project2/ap/final/ZipCatalog.txt"

def makeZipCatalog():
    import bz2
    print "PROFILE:[Total Time] TIMER STARTS"
    et = time.time(); ct = time.clock();
    indexhandle = open(zipIndexFilePath,'a')
    cataloghandle = open(zipCatalogFilePath,'a')
    termhashMaster = ["a","b","c",["d","e"],"f",["g","h","i"],["j","k","l"],"m","n","o","p","q","r","s","t","u","v",["w","x","y","z"],["0","1","2","3"],["4","5","6"],["7","8","9"]]
    for termstart in termhashMaster:
        if not isinstance(termstart,list):
            termstart = [termstart]
        termhash = {}
#       print "PROFILE:[ "+fname+" ] TIMER STARTS"
        e0 = time.time(); c0 = time.clock();
        for fname in os.listdir(INT_CORPUS_DIR):
            aFile = INT_CORPUS_DIR+"/"+fname
            docIndexHandle = open(aFile,'r')

            for line in docIndexHandle:
                term,postlst = str.split(line," ",1)
                term = term.strip();postlst = postlst.strip()
                if termhash.has_key(term):
                    plstInMap = termhash[term]
                    termhash[term]= plstInMap +" "+ postlst
                    plstInMap = ""
                elif term[0] in termstart:
                        termhash[term]=postlst
                        postlst = ""
                else: continue;
#            print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
#        indexhandle = open(indexFilePath,'a')
#        cataloghandle = open(catalogFilePath,'a')
#        print "PROFILE:[ Writing "+termstart+str(len(termhash))+" ] TIMER STARTS"
#        e0 = time.time(); c0 = time.clock();
        for term in termhash.keys():
            idxoffset = indexhandle.tell();
            com = bz2.BZ2Compressor().compress("{}  {}\n".format(term,termhash[term]))            
            
            indexhandle.seek(idxoffset)
            indexhandle.write("%s  %s\n"%(term,termhash[term]))
            cataloghandle.write("%s %s\n"%(term,idxoffset))
#        indexhandle.close();cataloghandle.close();
        termhash = {}
        print "**-->"+" ".join(termstart)+"<--***"
        print "PROFILE:[File writing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    indexhandle.close();cataloghandle.close();
#        exit(1)
    print "PROFILE:[Total ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))

catalogFilePath = "E:/NEU/Ir/Project2/ap/final/Catalog.txt"
CATALOG_PICKLE = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/CatalogPickle.dat"  

def makecataloghash():
#    doUnPickling("CATALOG", CATALOG_PICKLE)
    cataloghandle = open(catalogFilePath,'r')
    termSeekHash = {}
    for line in cataloghandle:
        term,seek = line.split()
        term = term.strip(); seek = int(seek.strip())
        termSeekHash[term] = seek
#    print termSeekHash
    return termSeekHash
      

seekHash = doUnPickling("CATALOG", CATALOG_PICKLE) ## Move this line outside for better query performance.       
def getIdxSeek(terms):
       
    termSeekMap = {}
    for term in terms:
        if seekHash.has_key(term):
            termSeekMap[term] = seekHash[term]
        else: termSeekMap[term] = -1
    return termSeekMap

def query(terms):
#    print "Check-1****",terms
    html = "<html><body>{}</body></html>"
    idxhandle = open(indexFilePath,'r')
    resultStr = ""
#    print "PROFILE:[InstancOf] TIMER STARTS"
#    et = time.time(); ct = time.clock();
    if not isinstance(terms,list):
        terms = [terms]
#    print "PROFILE:[InstanceOf ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
    seekHash = getIdxSeek(terms)
#    print "Check-2****",seekHash
    for term in terms:
#        print "PROFILE:[IndexSeek] TIMER STARTS"
#        et = time.time(); ct = time.clock();
        seek = seekHash[term]
#        print "PROFILE:[IndexSeek ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
        if not seek == -1:
#            print "PROFILE:[FIleOperation] TIMER STARTS"
#            et = time.time(); ct = time.clock()
            idxhandle.seek(seek)
            idxline = idxhandle.readline()
#            print "Index Line:",idxline
            idxterm,postlist = str.split(idxline," ",1)
#            print "Idxterm, postlist",idxterm,postlist
            if idxterm.strip()== term:
                resultStr += processPostings(postlist,"V")
            else:
                print "ERROR:--> Index seek location mismatch..."
                exit(1)
#            print "PROFILE:[FileOperation ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
        else:
            pre = "<PRE>\n{}\n</PRE>"
            corpusHeader = "%8s    %4s\n"%("ctf","df")
            corpusHeader = corpusHeader + "%8s    %4s\n"%("0","0") 
            resultStr = resultStr + pre.format(corpusHeader)
#    print resultStr
    idxhandle.close()
    return html.format(resultStr)
    
def processPostings(postStr,option):
#    postStr = re.sub(" ","\n",postStr)
#    postStr = re.sub(":","        ",postStr)
#    postStr = re.sub(","," ",postStr)
    pre = "<PRE>{}</PRE>"
    docStatlst = postStr.split()
    outV = "%8s   %4s    %5s    %s\n"%("docid","doclen","tf  ","posn")
    out = "%8s   %4s    %5s\n"%("docid","doclen","tf  ")
    corpusHeader = "%8s    %4s\n"%("ctf","df")
    df = len(docStatlst)
    ctf = 0
    for docStat in docStatlst:
        docId,doclen,tf,postlstStr= docStat.split(":")
        ctf += len(postlstStr.split(","))
#        print docId
        if option == "V":
#            "{0}        {1}        {2}    {3}".format(docId,doclen,tf,postlstStr)
            out = out + "%8s   %4s    %5s   %s\n"%(docId,doclen,tf,postlstStr)
        elif option == "v":
            out = out + "%8s   %4s    %5s\n"%(docId,doclen,tf)
    corpusHeader = corpusHeader + "%8s    %4s\n"%(ctf,df)
    result = pre.format(corpusHeader) +  pre.format(out)
#    docId = docStatlst[0]
#    print docStatlst
#    print out
    return result
    
                    
## findTermSeek: String String -> False/Int
## iterm is a term may be present in a file.
## catalog is of the format String:Int|String:Int            
#def findTermSeek(iterm,catalog):  
#    termSeekLst = catalog.split("|") 
#    termSeekMap = {}
#    for termSeek in termSeekLst:
#        term,seek = termSeek.split(":")
#        termSeekMap[term.strip()]=int(seek.strip())
#    if termSeekMap.has_key(iterm):
#        return termSeekMap[iterm]
#    else: return False

fileSeekMapPath = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/fileSeekMap.dat"
ctfTermMapFile = "E:\Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/termCtfMap.dat"
docLenFile = "E:/NEU/Ir/Project2/ap/final/DocLenMapping.txt"
ctfTermMapFileCheck = "E:/NEU/Ir/Project2/ap/final/termCtfMapFile.txt"


indexFilePath = "E:/NEU/Ir/Project2/ap/final/IndexFile.txt"
CORPUS_DIR = "E:/NEU/Ir/Project2/ap/ap"
INT_CORPUS_DIR = "E:/NEU/Ir/Project2/ap/out"    
     
STEM_PICKLE_FILE = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/stemPickle.dat"
STEM_FILE = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/stemr.txt"

STOPLIST_FILE = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/stoplist.txt"
STOPPICKLE_PATH = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/stopMapPickle.dat"

from PorterStemmer import PorterStemmer
p = PorterStemmer()

def doCleanStem(string):
    
#    print "docleanStem:",string
    words = string.split()
    words = removeContractions(words)
#    print "docleanStem:",len(words)
#    varsRootHash = doUnPickling("STEM_TEXT",STEM_PICKLE_FILE)#Move this line outside for faster stemming 
                           
    def mapfn(aword):
        aword = aword.strip()
#        print aword
        if not aword[0] in "0123456789":
#            if varsRootHash.has_key(aword):
            stemdword = p.stem(aword, 0,len(aword)-1)
            return stemdword
#            else:
#                return aword
        else: return aword
        
        
#    print words
    return map(mapfn,words)
        
#doIndex()
#makeCatalog()
#print query(["encrypt","about"])
makeZipCatalog()
