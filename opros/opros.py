#!/usr/bin/env python
# -*- coding: utf-8 -*-

from htmlTag import * 
from datetime import datetime
import cgi
import sys, os
import pickle


def cgiFieldStorageToDict( fieldStorage ):
    """Get a plain dictionary, rather than the '.value' system used by the cgi module."""
    params = {}
    for key in fieldStorage.keys():
        params[ key ] = fieldStorage.getlist(key)
        #print key
    return params

OPROS_NUM = "37"
LOCAL_DIR = "opros"
rootDir = "/home5/lhcsurve/www/opros/"+LOCAL_DIR+"/"
#fileName_opros = rootDir+"data/test.txt"
fileName_opros = rootDir+"data/opros_"+OPROS_NUM+".txt"

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


def CheckMissingAnswers(chb_list, dict, n_vop):
    # Check that all questions are answered (take care of checkboxes where it's not needed)
    missingData = []
    missingAnswers = []

    for nv in range(1,n_vop+1):
        if ('v'+str(nv) not in dict) and (nv not in chb_list):
            missingAnswers.append(nv)
            
    # Check that all the data is provided:
    if (dict["sex"]==['0']):
        missingData.append("Пол")
    if (dict["age"]==['0']):
        missingData.append("Возраст")
    if (dict["social"]==['0']):
        missingData.append("Социальный статус")

    return [missingAnswers, missingData]
        

def CompileOpros(unic):
    form = FORM(method="POST", action="opros.py")
    
    form <= INPUT(name="unic", type="hidden", value=unic)
    ip         = cgi.escape(os.environ["REMOTE_ADDR"])
    user_agent = cgi.escape(os.environ["HTTP_USER_AGENT"])
    form <= INPUT(name="ip", type="hidden", value=str(ip))
    form <= INPUT(name="user_agent", type="hidden", value=str(user_agent))
    form <= INPUT(name="time", type="hidden", value=str(datetime.utcnow()))
    #form <= DIV("Your IP: "+ str(ip))
    
    temp_ans_fileName = rootDir+'temp_ans_'+str(unic)+'.pkl'
    temp_ans = {}
    myOpros = ReadOpros(fileName_opros)

    tempAnsExists = False
    if os.path.exists(temp_ans_fileName):
        # If this file exists, then submit button was pressed, but not all questions were answered!
        temp_ans_file = open(temp_ans_fileName, 'rb')
        temp_ans = pickle.load(temp_ans_file)
        temp_ans_file.close()
        tempAnsExists = True

        warning = P("")
        missed = CheckMissingAnswers(myOpros[2], temp_ans, len(myOpros[0]))
        if len(missed[0])!=0:
            warning <= P(FONT("Вы не ответили на некоторые важные вопросы:", color="red")+"  №№ "+ str([v for v in missed[0] ]) )
            
        if len(missed[1])!=0:
            warning <= P(FONT("Необходимые данные о себе (для статистики) нужно ввести внизу опроса: ", color="red") +BR())
            for v in missed[1]:
                warning <= FONT(v+',  ', color="green")

        form <= warning
    

    vop = myOpros[0]   # this is a list of voprosov ["","vopros", "radio/checkbox"]
    otv = myOpros[1]   # list of lists of answers for each vopros
    n_vop =  len(vop)
    n_otv =  len(otv)
    #print "Kolichestvo oprosov = ", n_vop

    if(n_vop!=n_otv):
        form <= DIV("Kol-vo voprosov ne sovpadaet s otvetami")

    for v in range(0,n_vop):
        if v==6:
            form <= IMG(src="./img/quiz_37.jpg", align="right", border="1", hspace="25", vspace="5")
        form <= H3(str(v+1)+". "+vop[v][1])
        table = TABLE()
        if "radio" in vop[v][2]:
            for oo in range(0,len(otv[v])):
                # print otv[v][oo]
                if ('v'+str(v+1) in temp_ans) and (temp_ans['v'+str(v+1)][0]==str(oo+1)):
                    table <= TR(TD(LABEL(INPUT("&nbsp;"+otv[v][oo], type="radio", name="v"+str(v+1), value=str(oo+1), checked=True))))
                else:
                    table <= TR(TD(LABEL(INPUT("&nbsp;"+otv[v][oo], type="radio", name="v"+str(v+1), value=str(oo+1)))))
        elif "checkbox" in vop[v][2]:
            for oo in range(0,len(otv[v])):
                if ('v'+str(v+1) in temp_ans) and (str(oo+1) in temp_ans['v'+str(v+1)]):
                    table <= TR(TD(LABEL(INPUT("&nbsp;"+otv[v][oo], type="checkbox", name="v"+str(v+1), value=str(oo+1), checked=True))))
                else:
                    table <= TR(TD(LABEL(INPUT("&nbsp;"+otv[v][oo], type="checkbox", name="v"+str(v+1), value=str(oo+1)))))
        else:
            form <= DIV("Something is wrong here")
        form <= table

    form <= H3("Пару строк о себе:")
    
    sex_ans = ["Пол","М","Ж"]
    sel_sex = SELECT(name="sex")
    if tempAnsExists:
        for sa in [0,1,2]:
            if temp_ans["sex"][0]==str(sa):
                sel_sex <= OPTION(sex_ans[sa], selected=True, value=sa)
            else:
                sel_sex <= OPTION(sex_ans[sa], value=sa)
    else:    
        sel_sex <= OPTION("Пол", selected=True, value='0')
        sel_sex <= OPTION("М", value='1')
        sel_sex <= OPTION("Ж", value='2')

    
    form <= sel_sex +"&nbsp; &nbsp;"

    sel_age = SELECT(name="age")

    if ("age" in temp_ans) and temp_ans["age"][0]=='0':
        sel_age <= OPTION("Возраст", selected=True, value='0')
    else:
        sel_age <= OPTION("Возраст", value='0')
    
    for age in range(15,52):
        if (age==15):
            if ("age" in temp_ans) and temp_ans["age"][0]==str(age):
                sel_age <= OPTION('<='+str(age), selected=True, value=age)
            else:
                sel_age <= OPTION('<='+str(age),value=age)
        elif(age==51):
            if ("age" in temp_ans) and temp_ans["age"][0]== str(age):
                sel_age <= OPTION(str(age)+"+",selected=True, value=age)
            else:
                sel_age <= OPTION(str(age)+"+",value=age)
        else:
            if ("age" in temp_ans) and temp_ans["age"][0]== str(age):
                sel_age <= OPTION(age,selected=True, value=age)
            else:
                sel_age <= OPTION(age,value=age)

    form <= sel_age+BR()*2 +"&nbsp; &nbsp;"

    st_list = ["Школьник/Студент", \
               "Преподаватель/Аспирант",\
               "Офисный планктончег",\
               "Большой начальник",\
               "Свободный художник",\
               "Другое",]
    qual_list = ["  Этот опрос рулит!", "  Этот опрос отстой."]

    sel_social = SELECT(name="social")
    if ("social" in temp_ans) and (temp_ans["social"][0]=='0'):
        sel_social <= OPTION("Социальный статус", selected=True, value="0")
    else:
        sel_social <= OPTION("Социальный статус", value="0")
    for i in range(0,len(st_list)):
        if ("social" in temp_ans) and (temp_ans["social"][0]==str(i+1)):
            sel_social <= OPTION(st_list[i], selected=True, value=i+1)
        else:
            sel_social <= OPTION(st_list[i], value=i+1)
        
    form <= sel_social +BR()*3

    table = TABLE()
    table <= TR(TD(INPUT(type="submit", name="submit", value="Submit")) + TD(LABEL(INPUT(qual_list[0],type="radio", name="quality", value="1", checked = True))) )
    table <= TR(TD() + TD(LABEL(INPUT(qual_list[1], type="radio", name="quality", value="2"))))  
    form <= table

    #body <= CENTER(form)
    #body <= BR()*3
    #page =  HTML(head  + body)
    #fname = rootDir+"form.html"
    #f = open(fname,'w')

    print str(form).decode('utf-8').encode('cp1251')
    
    #print >>f, str(form).decode('utf-8').encode('cp1251')
    #print "Print file: \n\t "+fname


def ShowResults():
    results = DIV(FONT("Спасибо за ваш голос!",color="green"))

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
    
    for v in range(0,n_vop):
        #print "Vopros ", v+1, "Otvetov: ", len(otv[v])
        results <= H4(str(v+1)+". "+vop[v][1])
        if v==6:
            results <= IMG(src="./img/quiz_37.jpg", align="right", border="1", hspace="25", vspace="5")
        table = TABLE()
        colors = ["darkblue", "darkgreen", "darkred", "coral", "darkcyan", "orchid","goldenrod", "lightgreen", "silver","silver","silver"]
        for oo in range(0,len(otv[v])):
            percent = float(counts[v][oo])/N_votes
            percent_str = "%.1f" % (100*percent)
            table <= TR(TD(FONT("&nbsp;"+otv[v][oo], size="-1"))+TD(percent_str+"%"))
            table <= TR(TD(DIV("", style="height: 12px; width:"+ str(int(percent*400))+"px; background-color:"+ colors[oo]+";")))

        results <= table

    results <= DIV(2*BR()+"Всего проголосовало: "+FONT(str(N_votes),color="green"))

    #results <= DIV(str(datetime.utcnow()))
    
    #results <= DIV(str(counts))
    #results <= DIV(votes)

    print str(results).decode('utf-8').encode('cp1251')

def CheckRobotButton(unic):
    form = FORM(method="POST", action="opros.py")
    form <= H4(FONT("Подтвердите, что вы не робот:", color="green"))    
    form <= INPUT(name="unic", type="hidden", value=unic)

    form <= INPUT(type="submit", name="submit", value="Я не робот, пустите меня!")

    print str(form).decode('utf-8').encode('cp1251')
    


'''
Main part starts here
'''

getform = cgi.FieldStorage()
dict = cgiFieldStorageToDict(getform)

votes_fileName = rootDir+'votes.pkl'

UNIC = None

if (getform.getfirst("submit")=="Submit"):
    # submit button pressed!!

    isMissingAnswer = False
    isMissingData   = False

    myOpros = ReadOpros(fileName_opros)
    n_vop =  len(myOpros[0])
    
    temp_ans_fileName = rootDir+'temp_ans_'+dict["unic"][0]+'.pkl'
    #Make a list of checkboxes (question number)
    chb_list = myOpros[2]
    #Check that all questions are answered (take care of checkboxes where it's not needed)
    missed = CheckMissingAnswers(chb_list, dict, n_vop)
    if len(missed[0])!=0:
        isMissingAnswer = True
    if len(missed[1])!=0:
        isMissingData = True
        
    # If something is missing, refresh the page, but save the temp answers   
    if isMissingAnswer or isMissingData:
        '''
        print "Content-Type: text/html\n\n"
        print "<p> Not answered! </p>"
        print dict
        print isMissingAnswer, isMissingData
        print n_vop, [nv for nv in range(1, n_vop+1)]
        print "<br><br><br><br>"
        print "Creating temp file: ", temp_ans_fileName
        '''
        temp_ans_file = open(temp_ans_fileName, 'wb')
        pickle.dump(dict, temp_ans_file)
        temp_ans_file.close()

        print "Status: 303 See other"
        print "Location: /"+LOCAL_DIR
        print
        sys.exit(0)
        
    # Otherwise, it is a success! Reload the page (should show results now) and delete temp answers (important).
    else:
        '''
        print "Content-Type: text/html\n\n"
        print "<p> Success! </p>"
        print dict
        '''
        
        UNIC = getform.getfirst("unic")
        votes = {}
        if os.path.isfile(votes_fileName):
            votes_file = open(votes_fileName, 'rb')
            votes = pickle.load(votes_file)
            votes_file.close()

        votes_file = open(votes_fileName, 'wb')
        votes[UNIC] = dict
        pickle.dump(votes, votes_file)
        votes_file.close()

        #Remove temp_ans file
        if os.path.exists(temp_ans_fileName):
            #print "<br/><br/>deleting the file: ",temp_ans_fileName
            os.remove(temp_ans_fileName)
            
        print "Status: 303 See other"
        print "Location: /"+LOCAL_DIR
        print
        sys.exit(0)
elif (getform.getfirst("submit")!=None and getform.getfirst("submit")!="Submit"):
    print "Status: 303 See other"
    print "Location: /"+LOCAL_DIR
    print
    sys.exit(0)
    
else:
    if (len(sys.argv) == 1):
        print "Content-Type: text/html\n\n"
        print "<p>"
        print "Hey! You need to pass  unic\n"
        print dict
        print "</p>"
        sys.exit(0)
    if (len(sys.argv) > 1): UNIC = sys.argv[1]

    if UNIC=='0':
        CheckRobotButton(UNIC)
        sys.exit(0)

    if os.path.isfile(votes_fileName):
        votes_file = open(votes_fileName, 'rb')
        votes = pickle.load(votes_file)
        votes_file.close()
        #print votes
        
        if UNIC in votes:
        #if '0' in votes:
            ShowResults()
        else:
            CompileOpros(UNIC)
    else:
        CompileOpros(UNIC)



