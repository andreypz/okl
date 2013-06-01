#!/usr/bin/env python
# -*- coding: utf-8 -*-

from htmlTag import * 
from datetime import datetime
import sys, os
import pickle


#OPROS_NUM = "38"
LOCAL_DIR = "opros"
rootDir = "/home5/lhcsurve/www/opros/"+LOCAL_DIR+"/"

def ReadOpros(fName):
    
    a=0 
    vop = []   # this is a list of voprosov ["","vopros", "radio/checkbox"]
    otv = []   # list of lists of answers for each vopros

    f = open(fName)
    
    for line in f:
        if not line.strip():
            #print "whitie"
            continue
    
        if ("|" in line):
            otv.append([])
            a+=1
            columns = line.split('|')  # the output of the split method is
            vop.append(columns)
            #print a,line
        else:
            otv[a-1].append(line)        

    it = 0
    chb_list = []
    for nn in vop:
        it+=1
        if "checkbox" in nn[2]:
            chb_list.append(it)
        
    f.close()
    return [vop, otv, chb_list]

def ShowResults(OPROS_NUM):
    results = DIV(FONT("Опрос закончен. Результаты.",color="green"))

    votes_fileName = rootDir+'data/votes_'+OPROS_NUM+'.pkl'
    fileName_opros = rootDir+"data/opros_"+OPROS_NUM+".txt"
    myOpros = ReadOpros(fileName_opros)

    vop = myOpros[0]   # this is a list of voprosov ["","vopros", "radio/checkbox"]
    otv = myOpros[1]   # list of lists of answers for each vopros
    chb = myOpros[2]  # list. Numbers of questions that are checkboxes
    
    n_vop =  len(vop)
    n_otv =  len(otv)
    #print "Kolichestvo oprosov = ", n_vop

    counts = []
    
    votes = {}
    if os.path.isfile(votes_fileName):
        votes_file = open(votes_fileName, 'rb')
        votes = pickle.load(votes_file)
        votes_file.close()

        # counts contain the results as an array of counts for each choice
        
        for no_v in range(0,n_vop):
            counts.append([])
            for no_o in range(0,len(otv[no_v])):
                counts[no_v].append(0)

        for u,ans in votes.iteritems():
            #print u, ans
            for no_v in range(0,n_vop):
                if no_v+1 not in chb:
                    counts[no_v][ int(ans["v"+str(no_v+1)][0])-1] += 1
                else:
                    if "v"+str(no_v+1) in ans:
                        for cc in ans["v"+str(no_v+1)]:
                            counts[no_v][ int(cc)-1] += 1
    else:
        results <= DIV(FONT("Так, так, кажется у нас проблемки с отображением результатов. Сообщите о проблеме а каментах!", color="red"))

        
    N_votes = len(votes)
    #print "N_votes: ", N_votes
    
    for v in range(0,n_vop):
        #print "Vopros ", v+1, "Otvetov: ", len(otv[v])
        results <= H4(str(v+1)+". "+vop[v][1])
        if v==6:
            results <= IMG(src="../opros/img/quiz_"+OPROS_NUM+".jpg", align="right", border="1", hspace="25", vspace="5")
        table = TABLE()
        colors = ["darkblue", "darkgreen", "darkred", "coral", "darkcyan", "orchid","goldenrod", "lightgreen", "silver","silver","silver"]
        max_counts = max(counts[v])
        #results <= DIV("max_counts = " +str(max_counts))
        for oo in range(0,len(otv[v])):
            percent = float(counts[v][oo])/N_votes
            percent_str = "%.1f" % (100*percent)
            bar_width = 0
            if max_counts!=0:
                bar_width = 400.0*float(counts[v][oo])/max_counts
            table <= TR(TD(FONT("&nbsp;"+otv[v][oo], size="-1"))+TD(percent_str+"%"))
            table <= TR(TD(DIV("", style="height: 12px; width:"+ str(int(bar_width))+"px; background-color:"+ colors[oo]+";")))

        results <= table

    results <= DIV(2*BR()+"Всего проголосовало: "+FONT(str(N_votes),color="green"))

    #results <= DIV(str(datetime.utcnow()))
    #results <= DIV(str(counts))
    #results <= DIV(votes)

    print str(results).decode('utf-8').encode('cp1251')


''' 
Main part starts here
''' 
UNIC = 0;

if (len(sys.argv) == 1):
    print "Content-Type: text/html\n\n"
    print "<p>"
    print "Hey! You need to pass Unic \n"
    print dict
    print "</p>"
    sys.exit(0)
elif len(sys.argv) == 2:
    print "Content-Type: text/html\n\n"
    print "Hey! You need to pass  NUMBER \n"
    
elif (len(sys.argv)== 3):
    UNIC = sys.argv[1]
    OPROS_NUM = str(sys.argv[2])
else:
    print "Content-Type: text/html\n\n"
    print "Wrong \n"
    
ShowResults(OPROS_NUM)
   


