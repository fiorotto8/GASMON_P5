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
import argparse

if not os.path.exists("modified"):
    os.makedirs("modified")
if not os.path.exists("withHeader"):
    os.makedirs("withHeader")


ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="set the name of the dataset",default=None)
args = parser.parse_args()

##################################################
##################################################
##################################################
masked_days_string=["2021-10-31","2021-07-21","2021-07-22","2021-07-23","2021-07-24","2021-07-25","2021-07-26","2021-07-27","2021-07-28","2021-07-29","2021-07-30","2021-09-14","2021-10-21","2021-11-30","2021-11-24", "2022-03-10", "2022-03-27", "2022-02-17", "2022-02-16", "2022-03-11", "2022-03-12", "2022-03-13", "2022-03-14", "2022-03-15", "2022-03-16", "2022-03-17", "2022-03-23", "2022-03-28", "2022-04-13", "2022-04-14", "2022-04-15", "2022-04-16", "2022-04-17", "2022-04-18", "2022-04-19", "2022-04-20", "2021-12-09", "2021-12-10", "2021-12-11", "2021-12-12", "2021-12-13", "2021-12-14", "2021-12-15", "2021-12-16", "2021-12-17", "2021-12-18", "2021-12-19", "2021-12-20", "2021-12-21", "2021-12-22", "2021-12-23", "2021-12-24", "2021-12-25", "2021-12-26", "2021-12-27", "2021-12-28", "2021-12-29", "2021-12-30", "2021-12-31", "2022-01-01", "2022-01-02", "2022-01-03", "2022-01-04", "2022-01-05", "2022-01-06", "2022-01-07", "2022-01-08", "2022-01-09", "2022-01-10", "2022-01-11", "2022-01-12", "2022-01-13", "2022-01-14", "2022-01-15", "2022-01-16", "2022-01-17", "2022-01-18", "2022-01-19", "2022-01-20", "2022-01-21", "2022-01-22", "2022-01-23", "2022-01-24", "2022-01-25", "2022-01-26", "2022-01-27", "2022-01-28", "2022-01-29", "2022-01-30", "2022-01-31", "2022-02-01", "2022-02-02", "2022-02-03", "2022-02-04", "2022-02-05", "2022-02-06", "2022-02-07", "2022-02-08", "2022-02-09", "2022-02-10", "2022-02-11", "2021-11-25", "2021-11-26", "2021-11-27", "2021-11-28", "2021-11-29", "2021-11-30", "2021-12-01", "2021-12-02", "2021-12-03", "2021-12-04", "2021-12-05", "2021-12-06", "2021-12-07", "2021-12-08", "2021-12-09", "2021-10-22", "2021-10-21", "2021-10-23", "2021-10-24", "2021-10-25", "2021-10-26", "2021-10-27", "2021-10-28", "2021-10-29", "2021-10-30", "2021-10-31", "2021-11-01", "2021-11-02", "2021-11-03", "2021-11-04", "2021-11-05", "2021-11-06", "2021-11-07", "2021-11-08", "2021-11-09", "2021-11-10", "2021-11-11", "2021-11-12", "2021-11-13", "2021-11-14", "2021-11-15", "2021-11-16", "2021-11-17", "2021-11-18", "2021-11-19", "2021-11-20", "2021-11-21", "2021-11-22", "2021-11-23", "2021-11-24", "2021-09-21", "2021-09-22", "2021-09-23", "2021-09-24", "2021-09-25", "2021-09-26", "2021-09-27", "2021-09-28", "2021-09-29", "2021-09-30", "2021-10-01", "2021-10-02", "2021-10-03", "2021-10-04", "2021-10-05", "2021-10-06", "2021-10-07", "2021-10-08", "2021-10-09", "2021-10-10", "2021-10-11", "2021-10-12", "2021-10-13", "2021-10-14", "2021-10-15", "2021-10-16", "2021-10-17", "2021-10-18", "2021-10-19", "2021-10-20", "2021-10-21","2022-06-21","2022-07-18","2022-06-19", "2022-08-31","2022-10-29","2023-03-26","2023-04-14"]
##################################################
##################################################
##################################################
#masked_days_string=[]
max="2021-07-21"


#path of the orginal files
path="../All_data/logs"


def hist(list, x_name, channels=100, linecolor=4, linewidth=4):
    def fill_h(histo_name, array):
        for x in range (len(array)):
            histo_name.Fill((np.array(array[x] ,dtype="d")))

    array=np.array(list ,dtype="d")

    hist=ROOT.TH1D(x_name,x_name,channels,0.99*np.min(array),1.01*np.max(array))
    fill_h(hist,array)
    hist.SetLineColor(linecolor)
    hist.SetLineWidth(linewidth)
    hist.GetXaxis().SetTitle(x_name)
    hist.GetYaxis().SetTitle("Entries")
    hist.Write()
    hist.SetStats(False)
    hist.GetYaxis().SetMaxDigits(3);
    hist.GetXaxis().SetMaxDigits(3);
    #hist.Write()
    return hist

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

def graph(x,y,x_string, y_string, color=4, markerstyle=22, markersize=1):
        plot = ROOT.TGraph(len(x),  np.array(x  ,dtype="d")  ,   np.array(y  ,dtype="d"))
        plot.SetNameTitle(y_string+" vs "+x_string,y_string+" vs "+x_string)
        plot.GetXaxis().SetTitle(x_string)
        plot.GetYaxis().SetTitle(y_string)
        plot.SetMarkerColor(color)#blue
        plot.SetMarkerStyle(markerstyle)
        plot.SetMarkerSize(markersize)
        plot.Write()
        return plot

def rate_calc(timestamp):
#Calculate the hit rate of 55Fe source starting from a r0 measured @ start_date with second precision
#wite the date in %Y-%m-%d_%H:%M:%S format
#decay time is 1452.36 days or 12.55E9 seconds
#NB -> timestamp has to be a list also if it is one-sized
    def string_to_date(string):
        return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')

    start_date='2021-07-26_12:00:00'
    r0=3592.320833
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
    start_string="2022-05-05"
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

const_start=datetime.datetime.strptime('2022-05-05', '%Y-%m-%d')
if start<const_start:
    print("############################################")
    print("Start time should be after the 04/05/2022")
    print("############################################")
    sys.exit()

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
        outfile.write("Timestamp,Error Code,Error String,Mean Current,Mean Error,T,P,H,valve,flow set,flow read,syncro err flag,syncro time,Vset,Vmon,Imon,Status flag,Power,Error Message,Gain Measured,Gain Corrected,CO2,Gain mean,Gain err,t value,t flag\n")
        for index,line in enumerate(infile):
            outfile.write(line)

#list of paths of all the modified files
head=[]
for w in range(files_num):
    head.append(find(item[w]+"*", './withHeader'))
#print(len(mod))

#columns set on the modified data
col=["Timestamp", "Error Code", "Error String", "Mean Current", "Mean Error", "T", "P", "H","valve","flow set","flow read", "syncro err flag", "syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message","Gain Measured", "Gain Corrected", "CO2", "Gain mean","Gain err", "t value", "t flag" ]
#col=["Timestamp", "Error Code",	"Error String",	"Mean Current",	"Mean Error", "T", "P",	"H", "syncro err flag",	"syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message"]

#list of dataframes, every item is a daframe of one file
df=[]
for f in range(files_num):
    temp= pd.read_csv(head[f][0], delimiter=",", usecols=col)
    #print(head[f][0])
    #temp= pd.read_csv(head[f][0], delimiter=",")
    #print(temp.columns)
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
col=["Timestamp", "Error Code", "Error String", "Mean Current", "Mean Error", "T", "P", "H","valve","flow set","flow read", "syncro err flag", "syncro time", "Vset", "Vmon", "Imon", "Status flag", "Power", "Error Message","Gain Measured", "Gain Corrected", "CO2", "Gain mean","Gain err", "t value", "t flag" ]

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
"""
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

"""

#write dataframe
if args.name is None: result.to_csv("Dataset_"+start_string+"_"+end_string+".csv", sep=';', header=True, index=False, mode='w')
else: result.to_csv(args.name+".csv", sep=';', header=True, index=False, mode='w')



print("Step 4 OK")
print("###########################################################################################")

###################################################################################################################################################################

if args.name is None: main=ROOT.TFile("Dataset_"+start_string+"_"+end_string+".root","RECREATE")#root file creation
else: main=ROOT.TFile(args.name+".root","RECREATE")#root file creation
main.mkdir("variables_time")
main.cd("variables_time")

col=result.columns.tolist()


time=to_ROOT_arr(result["Timestamp"])
col.remove("Timestamp")
col.remove("Error String")
col.remove("Error Message")


ics=np.arange(0.,len(result[col[0]]), 1.)

plot = ROOT.TGraph(len(result["Timestamp"]),  time  ,   ics )
plot.GetXaxis().SetTimeDisplay(1);
plot.GetXaxis().SetTimeOffset(0);
plot.GetXaxis().SetNdivisions(5005);
plot.GetXaxis().SetTimeFormat("%d-%m-%y %H:%M");
plot.SetNameTitle("Calibration: points vs time","Calibration: points vs time")
plot.GetYaxis().SetTitle("Time (a.u.)")
plot.GetXaxis().SetTitle("Time")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.Write()


for i in range(len(col)):
    #print(col[i],result[col[i]])
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



graph(result["T"], result["Gain Corrected"],"Temperature", "Gain")
graph(result["P"], result["Gain Corrected"],"Pressure", "Gain")

graph(result["T"], result["t value"],"Temperature", "t value")
graph(result["P"], result["t value"],"Pressure", "t value")

main.mkdir("distributions")
main.cd("distributions")
for i in range(len(col)):

    hist(result[col[i]], col[i])

print("Step 5 OK")
print("###########################################################################################")









































#
#
#
#
#
#
