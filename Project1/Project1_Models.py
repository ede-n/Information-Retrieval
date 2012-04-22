'''
Created on May 10, 2011

@author: Naveen
'''
import time
import numpy as npy


#timeStamp = time.strftime("%H-%M-%S_%Y%m%d")
#logFile = open("log."+timeStamp,"w")
#debug = logFile.write

## makeUrl: ListOf<qTerm> -> String
## Given a ListOf<qTerm> returns the URL with ListOf<Term> in the query string.
def makeUrl(qid,lot):
    QPARAM_CONN = "&v="; DEFAULT_QSTRING = "d=3"
    HTTP_SERVER ="localhost:9999" #"fiji4.ccs.neu.edu";
    BASE_URL = "http://"+HTTP_SERVER+"/"#"http://"+ HTTP_SERVER +"/~zerg/lemurcgi/lemur.cgi"
    qstring = "v="+QPARAM_CONN.join(lot)#DEFAULT_QSTRING + QPARAM_CONN + QPARAM_CONN.join(lot)
    print "DEBUG:[makeUrl] [QID: %s]. %s" %(qid,qstring)
    return BASE_URL+"?"+qstring
    
    
## Version History
## 1.0 - created DataDefinition is as below
## getTermStatistics: ListOf<Terms> String -> {QTerm,(ctf,df)} {QTerm, {docID,(len,tf)}}
def getTermStatistics(lot, httpResp):
    import re
    stat_miss_terms = [] 
    docIdUniverse = {}
    patPre = "<\s*PRE\s*>\n\s*(.*?)\n</\s*PRE\s*>"
    pres = re.findall(patPre, httpResp,re.DOTALL)
#    print pres
    def process(listOflines):
        docid_present = True
        i=0; term = 1; qt_tf_len_hash = {};qt_ctf_df_hash = {};term_id_hash = {}
        for line in listOflines:
            if line.startswith("ctf"):
                pat = "(\d+)\s+(\d+)"
                ctf, df = re.findall(pat, line, flags=re.DOTALL)[0]
                print "ctf = %s   df = %s" %(ctf , df)
                if ctf == '0': 
                    docid_present = False
                    stat_miss_terms.append(lot[i])
                    print "*WARNING*:[getTermStatistics] Terms missing Statistics: \n",stat_miss_terms
                    i += 1
                else : 
                    docid_present = True
                    term_id_hash[lot[i]]= term
                    qt_ctf_df_hash[term] = (int(ctf),int(df))
                    i += 1
            elif line.startswith("docid"):
                vecPat = "(\d+)\s+(\d+)\s+(\d+)"
                k = re.findall(vecPat, line,flags=re.DOTALL)
                finalRes = {}
                for row in k:
                    docid, doclen, tf = row
                    finalRes[int(docid)]=(int(doclen),int(tf))
                    #collecting unique docIds for the given query
                    docIdUniverse[int(docid)]= (int (doclen)) 
                qt_tf_len_hash[term] = finalRes
                term += 1
        print "term_id_hash: ",term_id_hash
        return term_id_hash,docIdUniverse,qt_ctf_df_hash,qt_tf_len_hash
    return process(pres)

  
def getHttpRespString(url):
    print "Begin getHttpRespHtmlParserImpl -->"
    import urllib
    sock = urllib.urlopen(url)
    htmlsrc=sock.read()
    sock.close()
#    print htmlsrc
    return htmlsrc

# stem: List<qterms> -> {qterm:root}
# Statistics:
# Slight advantage over using map in cputime.
#TIMER: createCustomStemlist STARTS
#TIMER: createCustomStemlist ENDS
#Elapsed: 180.604000092  CPUTime: 1305840094.12  
def createCustomStemlist(uniq_qt):
    print "PROFILE:[createCustomStemlist] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    stem_file = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/stem-classes.lst"
    cust_stem_hash = {}
    stem_file_inmem = open(stem_file,"r")
    for stem_cl in stem_file_inmem:
        for qt in uniq_qt:
            root,vari = str.split(stem_cl,"|",1)
            variations = vari.strip().split()
            if qt == root.strip():
                continue;
            elif qt in variations:
                cust_stem_hash[qt]=root
#                print "%s  %s  %s" %(qt,root,vari)
    stem_file_inmem.close()
    print "PROFILE:[createCustomStemlist] TIMER  ENDS"
    print "PROFILE:[createCustomStemlist] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    print 'DEBUG:[createCustomStemlist] Stem roots for unique query terms:\n',cust_stem_hash
    return cust_stem_hash # the has contains 63 elements
    


## createStemmedQueries : -> {QueryID,List<qTerm>} 
## On the queries taken from queryfile
##   1. tokenize
##   2. Remove special characters
##   3. Filter stoplist
##   4. Apply Stemming to qTerms
def createStemmedQueries():
    queryTerms = {}
    qtLen = 0
    uniq_qTerms = []
    queries_file = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/desc.51-100.short"
    stoplist_file = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/stoplist.txt"
    #check if the following syntax autmatically calls .close on the open
    stoplist = [stopword.strip() for stopword in open(stoplist_file,"r")]
    contextStoplist = ["Document","report","discuss","describe","determine","predict","anticipate","identify","cite"]
    
    def applyStop(word):
        if word not in stoplist and \
            word not in contextStoplist:
            return True
        else: return False
    
    from re import sub
    info_needs = open(queries_file,"r")
    for info_need in info_needs:
        queryId,query = str.split(info_need,".",1)
#        print "ID: ",queryId;  print "Actual:",query.strip().split()
        query = sub("-"," ",query) # susbstitue - with a space
        query = sub("[.')(,\"]","",query)
#        print "No Pun:",query.strip().split()
        stoppedqlist = [str.lower(word) for word in query.strip().split() if applyStop(word)]
        #create a list of unique query terms so as to minimize the effor while stemming 
        for qt in stoppedqlist:
            if qt not in uniq_qTerms:
                uniq_qTerms.append(qt)   
        qtLen = qtLen + len(stoppedqlist)        
        queryTerms[queryId] = stoppedqlist        
    info_needs.close()
    
#    print "Stopped:",queryTerms
    print "DEBUG:[createStemmedQueries] Count of qterms: ", qtLen
    print "DEBUG:[createStemmedQueries] Count uniq qterms: ",len(uniq_qTerms)
    print "DEBUG:[createStemmedQueries] QueryTerms before stemming: \n",queryTerms
    ## modified the below implementation to porter stemmer
#    custom_stem_ref = createCustomStemlist(uniq_qTerms)
#    stemmedQueries = doStemming(custom_stem_ref,queryTerms)
    stemmedQueries = doStemming(None,queryTerms)
    print "DEBUG:[createStemmedQueries] QueryTerms after stemming: \n",stemmedQueries
    return stemmedQueries

# doStemming: {qTerm : root}  {QueryID,List<qTerm>} ->  {QueryID,List<qTerm>} 
#def doStemming(stemHash,qTermMaster):
#    qTermOutput = {}
#    print "PROFILE:[doStemming] TIMER STARTS"
#    e0 = time.time(); c0 = time.clock();
#    for qId in qTermMaster.keys():
#        qTList=[]
#        for qTerm in qTermMaster[qId]:
##            print "Before: ", qTerm
#            if qTerm in stemHash.keys():
#                qTerm = stemHash[qTerm]
##            print "After: ",qTerm
#            if qTerm.strip() not in qTList: qTList.append(qTerm.strip())
#        qTermOutput[qId]=qTList
#    print "PROFILE:[doStemming] TIMER ENDS"
#    print "PROFILE:[doStemming] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
#    return qTermOutput                  

from PorterStemmer import PorterStemmer
p = PorterStemmer()
## Porter stemer
def doStemming(stemHash,qTermMaster):
    
    qTermOutput = {}
    print "PROFILE:[doStemming] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    for qId in qTermMaster.keys():
        qTList=[]
        for qTerm in qTermMaster[qId]:
#            print "Before: ", qTerm
#            if qTerm in stemHash.keys():
            qTerm = p.stem(qTerm, 0,len(qTerm)-1)
#            print "After: ",qTerm
            if qTerm.strip() not in qTList: qTList.append(qTerm.strip())
        qTermOutput[qId]=qTList
    print "PROFILE:[doStemming] TIMER ENDS"
    print "PROFILE:[doStemming] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return qTermOutput 

def mapIntExtFile():
    print "PROFILE:[mapIntExtFile] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    intExtFileMapPath = "../res/doclist.txt"
    mapfile = open(intExtFileMapPath,"r")
    extfile_map_hash = {}
    for line in mapfile:
        if not line: break;
        intId,extId = line.strip().split()
        extfile_map_hash[intId.strip()] = extId.strip()        
    mapfile.close()
    print extfile_map_hash["25"]
    print "PROFILE:[mapIntExtFile] TIMER ENDS"
    print "PROFILE:[mapIntExtFile] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return extfile_map_hash

       

import os

def doPickling(option,pickleFile,loqt=None,url=""): 
    from pickle import Pickler  
    if os.path.isfile(pickleFile):
        os.remove(pickleFile)
        print "DEBUG:[doPickling] Removing existing pickleFile: ",pickleFile
    
    f = open(pickleFile,"w")
    if option == "STEMMED_QUERIES":
        print "DEBUG:[doPickling] Pickling Stemmed Queries..."
        stemmedQTList = createStemmedQueries() 
        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stemmedQTList
        p = Pickler(f)
        p.dump(stemmedQTList)
    elif option == "EXTFILE_MAP":
        print "DEBUG:[doPickling] Pickling file mappings..."
        extfile_map_hash = mapIntExtFile() 
        p = Pickler(f)
        p.dump(extfile_map_hash)
    elif option == "TERM_STATS":
        print "DEBUG:[doPickling] Pickling Query Statics..."
        httpRespString = getHttpRespString(url)
        term_id_hash,docIdUniverse,corpus_stats,query_stats = getTermStatistics(loqt,httpRespString)
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->QueryStats\n",query_stats
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->CorpusStats\n",query_stats
        p = Pickler(f) 
        p.dump(term_id_hash)
        p.dump(docIdUniverse)
        p.dump(corpus_stats)
        p.dump(query_stats)
    else: print "***ERROR***:[doPickling] Specify a correct option to UnPickle."
    f.close()


# doUnPickling: -> {qId,List<qTerm>}
def doUnPickling(option,pickleFile,loqt=None,url=""):
    from pickle import Unpickler
    if not os.path.isfile(pickleFile):
        print "DEBUG:[doUnPickling] PickleFile does not exist."
        doPickling(option,pickleFile,loqt,url)
    f = open(pickleFile,"r")
    if option == "STEMMED_QUERIES":
        up = Unpickler(f)
        unpkldData = up.load()
        f.close()
        print "DEBUG:[doUnPickling] Unpickled "+option+": "#,unpkldData
        return unpkldData  
    elif option == "EXTFILE_MAP":
        print "DEBUG:[doUnPickling] Unpickling ->"+option
        up = Unpickler(f)
        extfile_map_hash = up.load()
        f.close()
        return extfile_map_hash
    elif option == "TERM_STATS":
        print "DEBUG:[doUnPickling] Unpickling ->"+option
        up = Unpickler(f)
        term_id_hash = up.load()
        docIdUniverse = up.load()
        corpus_stats = up.load()
        query_stats = up.load()
        f.close()
#        print "DEBUG:[doUnPickling] Unpickled "+option+": corpus_stats",corpus_stats
#        print "DEBUG:[doUnPickling] Unpickled "+option+": query_stats",query_stats
        return term_id_hash,docIdUniverse,corpus_stats,query_stats
    else: print "***ERROR***:[doPickling] Specify a correct option to UnPickle."

# Unit testing:
#doUnPickling("EXTFILE_MAP","../res/int_ext_map.dat")

## vectorSpaceModel: {QTerm,(ctf,df)} {QTerm, {docID,(len,tf)}}
def vsmOktf(docIdUniverse,corpus_stats,term_stats,k=1.5,d=0.5):
    print "PROFILE:[vectorSpaceModel] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    #create doc Vector for each document.
    doc_vector_hash = []
    for docid in docIdUniverse.keys():
        doc_vector = []
        # approximation given in the problem, to use query length as doc length
        doc_len_appx = len(term_stats.keys())
        # creating a query vector with all ones meaning each query term is in this vector
        query_vector = npy.ones(doc_len_appx)
        for qterm in term_stats.keys():
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
#                OKTF=tf/(tf + 0.5 + 1.5*doclen/avgdoclen)
                inter_val = doclen/AVE_DOCLEN # trying actual doclen
                inter_val = inter_val * d
                oktf = npy.divide(tf,(tf + k + inter_val))
                doc_vector.append(oktf)
            else:doc_vector.append(0)
        #calculate the score which is cosine of angle between qry_vector and doc_vector
        npy_doc_vector = npy.array(doc_vector)
        numerator = npy.dot(npy_doc_vector,query_vector)#,npy.sqrt(npy.dot(npy_doc_vector,npy_doc_vector)))
        doc_vector_hash.append((docid,numerator))#npy.divide(numerator,npy.dot(npy_doc_vector,npy_doc_vector))))
#    print doc_vector_hash
    doc_vector_hash_sort = sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True) 
    print "DEBUG: [vectorSpaceModel] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[vectorSpaceModel] TIMER  ENDS"
    print "PROFILE:[vectorSpaceModel] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return doc_vector_hash_sort[:1000]


## vsmOktfIdf: {QTerm,(ctf,df)} {QTerm, {docID,(len,tf)}}
def vsmOktfIdf(docIdUniverse,corpus_stats,term_stats,k=1.5,d=0.5):
    print "PROFILE:[vectorSpaceModel] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    #create doc Vector for each document.
    doc_vector_hash = []
    for docid in docIdUniverse.keys():
        doc_vector = []
        # approximation given in the problem, to use query length as doc length
        doc_len_appx = len(term_stats.keys())
        # creating a query vector with all ones meaning each query term is in this vector
        query_vector = npy.ones(doc_len_appx)
#        query_vector = npy.multiply(query_vector,1+k+doc_len_appx/AVE_DOCLEN)
        for qterm in term_stats.keys():
            ctf,df = corpus_stats[qterm]
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
                idf = npy.log10(npy.divide(NUM_DOCS, df))
                #OKTF=tf/(tf + 0.5 + 1.5*doclen/avgdoclen)
                inter_val = doclen/AVE_DOCLEN # trying actual doclen
                inter_val = inter_val * d
                oktf = npy.divide(tf,(tf + k + inter_val))
                doc_vector.append(npy.multiply(oktf,idf))
            else:doc_vector.append(0)
        #calculate the score which is cosine of angle between qry_vector and doc_vector
        npy_doc_vector = npy.array(doc_vector)
        numerator = npy.dot(npy_doc_vector,query_vector)#,npy.sqrt(npy.dot(npy_doc_vector,npy_doc_vector)))
        doc_vector_hash.append((docid,numerator))#npy.divide(numerator,npy.dot(npy_doc_vector,npy_doc_vector))))
#    print doc_vector_hash
    doc_vector_hash_sort = sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True) 
    print "DEBUG: [vectorSpaceModel] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[vectorSpaceModel] TIMER  ENDS"
    print "PROFILE:[vectorSpaceModel] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return doc_vector_hash_sort[:1000]

import math as m
#{QTerm,(ctf,df)} {QTerm, {docID,(len,tf)}}
def LMWithLaplaceSmoothing(docIdUniverse,corpus_stats,term_stats):
    print "PROFILE:[LMWithLaplaceSmoothing] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    doc_vector_hash = []
    for docid in docIdUniverse.keys():
        totalProb = 0
        for qterm in term_stats.keys():
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
                totalProb += m.log10((tf + 1)/float(doclen + NUM_UNIQUE_TERMS))
            else:
                totalProb += m.log10(1/float(docIdUniverse[docid]+NUM_UNIQUE_TERMS))
#                print "DEBUG: [LMWithLaplaceSmoothing] TProb: raw %s Decimal %s" %(str(totalProb),str(Decimal(totalProb)))
        doc_vector_hash.append((docid,totalProb))
#    print doc_vector_hash
    doc_vector_hash_sort = sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True)[:1000] 
#    print "DEBUG: [LMWithLaplaceSmoothing] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[LMWithLaplaceSmoothing] TIMER  ENDS"
    print "PROFILE:[LMWithLaplaceSmoothing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return doc_vector_hash_sort


def JMSmoothing(docIdUniverse,corpus_stats,term_stats):
    print "PROFILE:[JMSmoothing] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    doc_vector_hash = []
    rawWt = 0.8
    bgWt = 0.2
    for docid in docIdUniverse.keys():
        totalProb = 0
        for qterm in term_stats.keys():
            ctf,df = corpus_stats[qterm]
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
#                print "qterm:%s docid:%s tf:%s ctf:%s doclen:%s" %(str(qterm), str(docid),str(tf),str(ctf),str(doclen))
                P = float(tf)/float(doclen)
                Q = float(ctf)/float(NUM_TERMS)
                totalProb += m.log10( rawWt*P + bgWt*Q) 
            else:
                Q = float(ctf)/float(NUM_TERMS)
                totalProb += m.log10(bgWt*Q)          
#                print "DEBUG: [JMSmoothing] TProb: raw %s Decimal %s" %(str(totalProb),str(Decimal(totalProb)))
        doc_vector_hash.append((docid,totalProb))
#    print doc_vector_hash
    #    print "DEBUG: [JMSmoothing] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[JMSmoothing] TIMER  ENDS"
    print "PROFILE:[JMSmoothing] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return  sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True)[:1000] 


def DirichletLM(docIdUniverse,corpus_stats,term_stats):
    print "PROFILE:[DirichletLM] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    doc_vector_hash = []
    
    
    # lambda = N/(N+u) the value of u is 2000 and N is the length of document.
    for docid in docIdUniverse.keys():
        totalProb = 0
        for qterm in term_stats.keys():
            ctf,df = corpus_stats[qterm]
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
                rawWt = float(doclen/(doclen + AVE_DOCLEN))
                bgWt = 1 - rawWt
#                rawWt = float(NUM_TERMS/(NUM_TERMS + 2000))
#                print "qterm:%s docid:%s tf:%s ctf:%s doclen:%s" %(str(qterm), str(docid),str(tf),str(ctf),str(doclen))
                P = float(tf)/float(doclen)
                Q = float(ctf)/float(NUM_TERMS)
                totalProb += m.log10( rawWt*P + bgWt*Q) 
            else:
                doclen = docIdUniverse[docid]
                bgWt = 1- float(doclen/(doclen + AVE_DOCLEN))
                Q = float(ctf)/float(NUM_TERMS)
                totalProb += m.log10(bgWt*Q)          
#                print "DEBUG: [JMSmoothing] TProb: raw %s Decimal %s" %(str(totalProb),str(Decimal(totalProb)))
        doc_vector_hash.append((docid,totalProb))
#    print doc_vector_hash
    #    print "DEBUG: [JMSmoothing] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[DirichletLM] TIMER  ENDS"
    print "PROFILE:[DirichletLM] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return  sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True)[:1000] 


## vsmOktfIdf: {QTerm,(ctf,df)} {QTerm, {docID,(len,tf)}}
def bm25(docIdUniverse,corpus_stats,term_stats):
    # BM25 extends binary independence to include document and query term weights.
    # A = [(r + 0.5)/(R - r + 0.5)]/[(n - r + 0.5)/(N - n - R + r + 0.5)]
    # B = [(k1 + 1)* tf]/[K + tf] where K = k1*[(1-b) + b * (doclen/Avg_doclen)]
    # C = [(k2 + 1)*qf]/[k2 + qf]
    # BM25 = log(A * B * C)
    # k1 = 1.2 - determines how the tf component of the term weight changes as tf increases.
    # b = 0.75 - regulates the impact of length normalization. b=0 means no length normalization
    # qf is assumed to be 1.
    print "PROFILE:[bm25] TIMER STARTS"
    e0 = time.time(); c0 = time.clock();
    #create doc Vector for each document.
    doc_vector_hash = []
    for docid in docIdUniverse.keys():
        bm25perdoc = 0
        # approximation given in the problem, to use query length as doc length
        for qterm in term_stats.keys():
            ctf,df = corpus_stats[qterm]
            A = (NUM_DOCS - df + 0.5)/(df + 0.5)
            if term_stats[qterm].has_key(docid):
                doclen,tf = term_stats[qterm][docid]
                B = float(2.2*tf/(0.3 + tf + 0.9 * float(doclen / AVE_DOCLEN)))
                bm25perdoc += npy.log10(A*B)
            else:bm25perdoc 
        doc_vector_hash.append((docid,bm25perdoc))
#    print doc_vector_hash
    doc_vector_hash_sort = sorted(doc_vector_hash,key=lambda atpl:atpl[1],reverse=True) 
    print "DEBUG: [bm25] Total number of docs ranked ->",len(doc_vector_hash)
    print "PROFILE:[bm25] TIMER  ENDS"
    print "PROFILE:[bm25] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
    return doc_vector_hash_sort[:1000]
    
    


stemdQTPickleURI = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/stemdQPicle.dat"
extFileMappingURI = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/int_ext_map.dat"
#NUM_DOCS = 84678;NUM_TERMS = 24401877; NUM_UNIQUE_TERMS = 166054; AVE_DOCLEN = 288;
NUM_DOCS = 84678;NUM_TERMS = 22997061; NUM_UNIQUE_TERMS = 171230; AVE_DOCLEN = 272;
OKTFIDF = "OKTFIDF";OKTF= "OKTF";LPM = "LP";JMM = "JM";DCL = "DCL"; BM25 = "BM25"

def run(model=OKTFIDF):
    stemdQList = doUnPickling("STEMMED_QUERIES",stemdQTPickleURI)
    #doPickling("TERM_STATS","../res/60.dat",["side"],"http://fiji4.ccs.neu.edu/~zerg/lemurcgi/lemur.cgi?d=3&v=side")
    if model == OKTF: outFilePre = "OKTF_"
    elif model == OKTFIDF: outFilePre = "OKTFIDF_"
    elif model == LPM: outFilePre = "LP_"
    elif model == JMM: outFilePre = "JM_"
    elif model == BM25: outFilePre = "BM25_"
    elif model == DCL: outFilePre = "DCL_"
#    outputURI = "E:/NEU/Ir/Project1/Output/"+outFilePre+time.strftime("%d%b%Y_%H_%M_%S", time.localtime())+".txt"
    outputURI = "E:/NEU/Ir/Project2/ap/models/"+outFilePre+time.strftime("%d%b%Y_%H_%M_%S", time.localtime())+".txt"
    file = open(outputURI,'a')
    
    for qid in sorted(map(lambda akey:int(akey),stemdQList.keys())):
            print "qid: "+str(qid)
#        if qid == "85":
            loqt = stemdQList[str(qid)]
            url = makeUrl(str(qid),loqt)
            qryPickleURI = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/res/"+str(qid)+".dat"
#            outputURI = "E:/NEU/Ir/Project1/Output/"+qid+"_"+model+"_output.txt"
            print qryPickleURI
            term_id_hash,docIdUniversePerQry,corpus_stats,query_stats = doUnPickling("TERM_STATS",qryPickleURI,loqt,url)
#            continue
        #    print "Term_ID_hash: ",term_id_hash
        #    print "corpus_stats: ", corpus_stats
        #    print "query_stats: ",query_stats[1]
        #    print "docIdUinverse: ",docIdUniversePerQry
        #    print "corpus_stats: ",corpus_stats
            print "docIdUniverse length: ", len(docIdUniversePerQry)
            extfile_map_hash = doUnPickling("EXTFILE_MAP",extFileMappingURI)
#            k=2.82;d=1.8; #2.82<k3.4 , 1.8 < d < 2.3
#            for k in [3.0,3.2,3.4]:
#                for d in [2.3]:
            if model == OKTFIDF:
                ranked_list = vsmOktfIdf(docIdUniversePerQry,corpus_stats,query_stats)
            elif model == OKTF:
                ranked_list = vsmOktf(docIdUniversePerQry,corpus_stats,query_stats)
            elif model == LPM:
                ranked_list = LMWithLaplaceSmoothing(docIdUniversePerQry, corpus_stats, query_stats)
            elif model == JMM:
                ranked_list = JMSmoothing(docIdUniversePerQry, corpus_stats, query_stats)
            elif model == BM25:
                ranked_list = bm25(docIdUniversePerQry, corpus_stats, query_stats)
            elif model == DCL:
                ranked_list = DirichletLM(docIdUniversePerQry, corpus_stats, query_stats)
#            print str(qid)+"",ranked_list[:50]
        #            print ranked_list
#            outputURI = "E:/NEU/Ir/Project1/Output/"+qid+"_k-"+str(k)+"_d-"+str(d)+"output.txt"
#            file = open(outputURI,'a')
            rank_counter = 1
            for intId,score in ranked_list:
                file.write("%s\tQ0\t%s\t%s\t%s\tExp\n" %(str(qid),extfile_map_hash[str(int(intId))],rank_counter,str(score)))
                rank_counter += 1  
            
#                    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"+ qid + time.asctime()+"K:"+str(k)+"D:"+str(d)+"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
             
            print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"+ str(qid) + time.asctime()+"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"     
#            import sys
#            sys.exit(1)
#        else: continue
    file.close()


print "PROFILE:[COMPLETE OPERATION] TIMER STARTS"
e0 = time.time(); c0 = time.clock();
#run(model = OKTFIDF)
#run(model = OKTF)
run(model = LPM)
run(model = JMM)
run(model = BM25)
#run(model = DCL)

print "PROFILE:[COMPLETE OPERATION] TIMER  ENDS"
print "PROFILE:[COMPLETE OPERATION] ElapsedTime: %s  CPUTime: %s" %(str(time.time()-e0),str(time.time()-c0))
