import pandas as pd
import os
import datetime
import subprocess
import sys
import fnmatch
import numpy as np
import math as m
import ROOT
from array import array
import glob

##################################################
##################################################
##################################################
masked_days_string=["2021-10-31","2021-07-21","2021-07-22","2021-07-23","2021-07-24","2021-07-25","2021-07-26","2021-07-27","2021-07-28","2021-07-29","2021-07-30","2021-09-14","2021-10-21","2021-11-30","2021-11-24"]
##################################################
##################################################
##################################################

max="2021-07-21"

#path of the orginal files
path="../../All_data/logs"

def nparr(string):
    return np.array(string, dtype="d")

def d_to_s(date):
    return str(date.strftime("%Y-%m-%d"))

def s_to_d(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d')

def find(pattern, path):
    """function that find a file by the pattern in the path"""
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    return result

def rate_calc(timestamp):
#Calculate the hit rate of 55Fe source starting from a r0 measured @ start_date with second precision
#wite the date in %Y-%m-%d_%H:%M:%S format
#decay time is 1452.36 days or 12.55E9 seconds
#NB -> timestamp has to be a list also if it is one-sized
    def string_to_date(string):
        return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')

    start_date='2022-10-11_12:00:00'
    r0=2597.9125
    #r0=300
    tau=1.255E8#seconds

    rate=np.empty(len(timestamp))

    for i in range(len(timestamp)):
        dt=(string_to_date(timestamp[i])-string_to_date(start_date)).total_seconds()
        rate[i]=r0*m.exp(-dt/tau)

    return rate

def to_ROOT_arr(list):
    "Convert current timestamp to ROOT feasible time axis"
    x=array('d')
    for i in list:
        year=int(i[0:4])
        month=int(i[5:7])
        day=int(i[8:10])
        hour=int(i[11:13])
        minute=int(i[14:16])
        second=int(i[17:19])
        #print(year, month, day, hour, minute, second)
        dat=ROOT.TDatime(year, month, day, hour, minute, second)
        x.append( int( dat.Convert() ) )
    return x


n0=200
e=1.6E-19
print("###########################################################################################")

#
#
#
#1) Count the available files and produce thedatetime objects and strings of the dates
#2) attach header on files, write them on a folder and save a csv with all the data
#3) from the files with headers removed selected bad lines and write all the data on csv
#4) with the value of the rate, write a compressed dataframe with gain and env par
#
#
#

######################################################################################################################################################################################
#1)

print("If you want to mask some days you need to insert them at the very beginning of this code")
start_string = input("PLS provide START string 'yyyy-mm-dd' write 'max' for taking the oldest: ")
if start_string=="max":
    start_string=max
else:
    start_string = str(start_string)
end_string = (input("PLS provide STOP string 'yyyy-mm-dd' write 'max' for taking the newest: "))
if end_string=="max":
    end_string=str((datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
else:
    end_string = str(end_string)
"""
#start_string=input("Type start date in this format: %YYYY-%MM-%dd: ")
#start_string="2021-09-22"#a valle bello
start_string="2021-10-22"#a monte bello
#start_string="2021-08-01"
#end_string=str((datetime.date.today()-datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
#end_string="2021-10-20"#a valle bello
end_string=str((datetime.date.today()).strftime("%Y-%m-%d"))
"""

masked_days=[ s_to_d(x) for x in masked_days_string]

#convert the start and stop string to the start and stop datetime
start = datetime.datetime.strptime(start_string, '%Y-%m-%d')
end = datetime.datetime.strptime(end_string, '%Y-%m-%d')

print("Start date is:",start)
print("End date is:", end)

diff=end - start
files_num=diff.days+1

print("There are",files_num, "files")
#print("The dates of the available files are:")

#create the datetimes of all the files involved
date_list = [start + datetime.timedelta(days=x)  for x in range(files_num)]

print("All days: ", len(date_list))

for x in range(len(masked_days)):
    while masked_days[x] in date_list:
        date_list.remove(masked_days[x])

print("All days after masking: ", len(date_list))

#files_num=diff.days+1-len(masked_days)
files_num=len(date_list)

#convert the datetimes objects to string for find the files
item=[]
for x in range(files_num):
    item.append(str(date_list[x].strftime("%Y-%m-%d")))
    #print("cacca",item[x])

#create list of paths of all the files to attach
logs=[]
for w in range(files_num):
    logs.append(find(item[w]+"*", path))
    #print(w, logs[w])

print("###########################################################################################")
print("Step 1 OK")
print("###########################################################################################")

######################################################################################################################################################################################
#2)

#print("ANO")
#this cycle opens all the files on the list and create new ones
#in the directory /withHeader with the headers
for j in range(files_num):
    #print(logs[j][0])
    infile = open(logs[j][0],'r').readlines()
    #print(infile)
    #print("ANO")

    with open("./withHeader/"+str(date_list[j].strftime("%Y-%m-%d"))+".txt",'w') as outfile:
        #outfile.write("Timestamp,Error Code,Error String,Mean Current,Mean Error,T,P,H,syncro err flag,syncro time,Vset,Vmon,Imon,Status flag,Power,Error Message\n")
        outfile.write("Timestamp,Error Code,Error String,Mean Current,Mean Error,T,P,H,valve,flow set,flow read,syncro err flag,syncro time,Vset,Vmon,Imon,Status flag,Power,Error Message\n")
        for index,line in enumerate(infile):
            outfile.write(line)

#list of paths of all the modified files
head=[]
for w in range(files_num):
    head.append(find(item[w]+"*", './withHeader'))
#print(len(mod))

#columns set on the modified data
col=["Timestamp", "Error Code", "Error String", "Mean Current", "Mean Error", "T", "P", "H","valve","flow set","flow read", "syncro err flag", "syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message" ]
#col=["Timestamp", "Error Code",	"Error String",	"Mean Current",	"Mean Error", "T", "P",	"H", "syncro err flag",	"syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message"]

#list of dataframes, every item is a daframe of one file
df=[]
for f in range(files_num):
    temp= pd.read_csv(head[f][0], delimiter=",", usecols=col)
    #print(temp)
    df.append(temp)



result=pd.concat(df, axis=0, join='outer', ignore_index=False, keys=None,levels=None, names=None, verify_integrity=False, copy=True)

#print(result)
#result.to_csv("AllData-concatenated.csv", sep=';', header=True, index=False, mode='w')

print("Step 2 OK")
print("###########################################################################################")

######################################################################################################################################################################################
#3)

#put in this list a string contained in the lines to remove
bad_word=["Start_run", "Stop_run", "TIMEOUT", "9.900000E+35", " VSET(-1)_VMON(-1)_ISET(-1)_IMON(-1)_STAT(-1)_"]

#this cycle opens all the files on the list and create new ones
#in the directory /modified without the lines that contains the
#strings in the bad_word list
for j in range(files_num):
    infile = open(head[j][0],'r').readlines()
    #print(j)

    with open("./modified/"+str(date_list[j].strftime("%Y-%m-%d"))+".txt",'w') as outfile:
        for index,line in enumerate(infile):
            if not any(bad_word in line for bad_word in bad_word):
                outfile.write(line)

#list of paths of all the modified files
mod=[]
for w in range(files_num):
    mod.append(find(item[w]+"*", './modified'))
#print(len(mod))

#columns set on the modified data
col=["Timestamp", "Error Code", "Error String", "Mean Current", "Mean Error", "T", "P", "H","valve","flow set","flow read", "syncro err flag", "syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message" ]

#list of dataframes, every item is a daframe of one file
df=[]
for f in range(files_num):
    temp= pd.read_csv(mod[f][0], delimiter=",", usecols=col)
    #print(temp)
    df.append(temp)


result=pd.concat(df, axis=0, join='outer', ignore_index=False, keys=None,levels=None, names=None, verify_integrity=False, copy=True)

#print(result)
#result.to_csv("Dataset_"+start_string+"_"+end_string+".csv", sep=';', header=True, index=False, mode='w')

print("Step 3 OK")
print("###########################################################################################")



#5)
#points=np.array([x for x in range(len(result["Mean Current"]))],dtype="d"  )

timestamps=result["Timestamp"].tolist()
rate=rate_calc(timestamps)
erate=np.sqrt(rate*60)/60
gain=-1*nparr(result["Mean Current"])/(n0*e*rate)
egain=gain*np.sqrt(np.square(erate/rate)+np.square(nparr(result["Mean Error"])/nparr(result["Mean Current"])))
#print(rate)


result.insert(5, "Rate", rate, True)
result.insert(6, "err Rate", erate, True)
result.insert(7, "Gain", gain, True)
result.insert(8, "err gain", egain, True)



#write dataframe
result.to_csv("Dataset_"+start_string+"_"+end_string+".csv", sep=';', header=True, index=False, mode='w')



print("Step 4 OK")
print("###########################################################################################")

###################################################################################################################################################################


main=ROOT.TFile("Dataset_"+start_string+"_"+end_string+".root","RECREATE")#root file creation


col=result.columns.tolist()


time=to_ROOT_arr(result["Timestamp"])
col.remove("Timestamp")
col.remove("Error String")
col.remove("Error Message")






for i in range(len(col)):

    plot = ROOT.TGraph(len(result[col[0]]),  time  ,   nparr(result[col[i]]) )
    plot.GetXaxis().SetTimeDisplay(1);
    plot.GetXaxis().SetTimeOffset(0);
    plot.GetXaxis().SetNdivisions(5005);
    plot.GetXaxis().SetTimeFormat("%d-%m-%y %H:%M");
    plot.SetTitle(col[i]+" vs time")
    plot.SetName(col[i]+" vs time")
    plot.GetXaxis().SetTitle("Time")
    plot.GetYaxis().SetTitle(col[i])
    plot.SetMarkerColor(4)#blue
    plot.SetMarkerStyle(22)
    plot.SetMarkerSize(1)
    plot.Write()

print("Step 5 OK")
print("###########################################################################################")

















































#
#
#
#
#
#
