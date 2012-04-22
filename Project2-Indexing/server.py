## Echo server program
#import socket
#
#HOST = ''                 # Symbolic name meaning all available interfaces
#PORT = 50007              # Arbitrary non-privileged port
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.bind((HOST, PORT))
#s.listen(1)
#conn, addr = s.accept()
#print 'Connected by', addr
##while 1:
#data = conn.recv(2048)
#print "Data",data
##    if not data: break
#conn.send("<html><body><h1>Hello python!!</h1></body></html>")
#conn.close()

import SocketServer,os,time



def doPickling(option,pickleFile,obj=None):
    varRootHash = {} 
    from pickle import Pickler  
    if os.path.isfile(pickleFile):
        os.remove(pickleFile)
        print "DEBUG:[Pickling] Removing existing pickleFile: ",pickleFile
    f = open(pickleFile,"w")
    if option == "CATALOG" :
        print "DEBUG:[Pickling] Pickling CATALOG..."
        fileSeekHash = obj 
#        print "DEBUG:[doPickling] Before dumping to"+pickleFile+"->\n",stemmedQTList
        p = Pickler(f)
        p.dump(makecataloghash())
        f.close()
    else:
        print "******ERROR******* Specify correct pickle option"

def doUnPickling(option,pickleFile):
    varRootHash = {}
    from pickle import Unpickler
    if not os.path.isfile(pickleFile):
        print "DEBUG:[doUnPickling] PickleFile does not exist."
        if option == "TERM_CTFMAP":
            print "****ERROR Unpickling****"; exit(1)
        doPickling(option,pickleFile)
    f = open(pickleFile,"r")
    if option == "CATALOG" :
        print "DEBUG:[doUnpickling] UnPickling Catalog.."
        up = Unpickler(f)
        termSeekHash = up.load()
        f.close()
        return termSeekHash
    else:
        print "******ERROR******* Specify correct pickle option"

catalogFilePath = "E:/NEU/Ir/Project2/ap/final/Catalog.txt"
CATALOG_PICKLE = "E:/Learning Passion/Programming Languages/Python/Projects/HelloPython/src/Proj2Pickles/CatalogPickle.dat"  
indexFilePath = "E:/NEU/Ir/Project2/ap/final/IndexFile.txt"

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
    html = "<html><body>{}</body></html>"
    idxhandle = open(indexFilePath,'r')
    resultStr = ""
#    print "PROFILE:[InstancOf] TIMER STARTS"
#    et = time.time(); ct = time.clock();
    if not isinstance(terms,list):
        terms = [terms]
#    print "PROFILE:[InstanceOf ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
    seekHash = getIdxSeek(terms)
    print "SeekHash",seekHash
    for term in terms:
#        print "PROFILE:[IndexSeek] TIMER STARTS"
#        et = time.time(); ct = time.clock();
        seek = seekHash[term]
#        print "PROFILE:[IndexSeek ElapsedTime]: %s  CPUTime: %s" %(str(time.time()-et),str(time.time()-ct))
        
        if not seek == -1:
#            print "PROFILE:[FIleOperation] TIMER STARTS"
            et = time.time(); ct = time.clock()
            idxhandle.seek(seek)
            idxline = idxhandle.readline()
#            print "Index Line:",idxline
            idxterm,postlist = str.split(idxline," ",1)
#            print "Idxterm, postlist",idxterm,postlist
            if idxterm.strip()== term:
#                print "RESULTSTR== %s\n%s"%(term,resultStr)
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
    idxhandle.close()
    return html.format(resultStr)
    
def processPostings(postStr,option):
    pre = "<PRE>\n{}\n</PRE>"
    docStatlst = postStr.split()
    outV = "%8s   %4s    %5s    %s\n"%("docid","doclen","tf  ","posn")
    outv = "%8s   %4s    %5s\n"%("docid","doclen","tf  ")
    if option == "V": out = outV
    else: out = outv
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
    return result

class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.
    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote:" % self.client_address[0]
        qryStr = self.data.split("\n")[0].split()[1]
        paramslst = qryStr[2:]
        params = paramslst.split("&")
        self.qtermlst = [p[2:] for p in params]
        # just send back the same data, but upper-cased
#        if len(self.qtermlst)> 0:
#            if not self.qtermlst[0] == "icon.ico":
        print self.qtermlst
        self.request.send(query(self.qtermlst))
#            else:
#                print self.qtermlst
                

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()