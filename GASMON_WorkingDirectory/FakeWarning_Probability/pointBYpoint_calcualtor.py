import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m
import datetime
import sys
import tqdm
import sys
import awkward
import uproot
import math as m
import os
from scipy import stats

def nparr(string):
    return np.array(string, dtype="d")

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

#define filling histogram function
def fill_h(histo_name, array):
    for x in range (len(array)):
        histo_name.Fill((np.array(array[x] ,dtype="d")))

def grapherr(x,y,ex,ey,x_string, y_string, color=4, markerstyle=22, markersize=1):
        plot = ROOT.TGraphErrors(len(x),  np.array(x  ,dtype="d")  ,   np.array(y  ,dtype="d") , np.array(   ex   ,dtype="d"),np.array( ey   ,dtype="d"))
        plot.SetNameTitle(y_string+" vs "+x_string,y_string+" vs "+x_string)
        plot.GetXaxis().SetTitle(x_string)
        plot.GetYaxis().SetTitle(y_string)
        plot.SetMarkerColor(color)#blue
        plot.SetMarkerStyle(markerstyle)
        plot.SetMarkerSize(markersize)
        plot.Write()
        return plot

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

def canvas(plot, size=800, leftmargin=0.1, rightmargin=0.2):
    y_name=plot.GetYaxis().GetTitle()
    x_name=plot.GetXaxis().GetTitle()
    can1=ROOT.TCanvas(y_name+" vs "+x_name,y_name+" vs "+x_name, size, size)
    can1.SetFillColor(0);
    can1.SetBorderMode(0);
    can1.SetBorderSize(2);
    can1.SetLeftMargin(leftmargin);
    can1.SetRightMargin(rightmargin);
    can1.SetTopMargin(0.1);
    can1.SetBottomMargin(0.1);
    can1.SetFrameBorderMode(0);
    can1.SetFrameBorderMode(0);
    can1.SetFixedAspectRatio();

    plot.Draw("ALP")

    can1.Write()
    can1.SaveAs(y_name+" vs "+x_name+".png")
    return can1

def hist(list, x_name, channels=100, linecolor=4, linewidth=4):
    def fill_h(histo_name, array):
        for x in range (len(array)):
            histo_name.Fill((np.array(array[x] ,dtype="d")))

    array=np.array(list ,dtype="d")

    hist=ROOT.TH1D(x_name,x_name,channels,0.9*np.min(array),1.1*np.max(array))
    fill_h(hist,array)
    hist.SetLineColor(linecolor)
    hist.SetLineWidth(linewidth)
    hist.GetXaxis().SetTitle("Gain")
    hist.GetYaxis().SetTitle("Entries")
    hist.Write()
    hist.SetStats(False)
    hist.GetYaxis().SetMaxDigits(3);
    hist.GetXaxis().SetMaxDigits(3);
    #hist.Write()
    return hist


print("#################################################################################################################")
print("         Chose the REFERENCE dataset: ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../TP_correction/*.csv")
print("#################################################################################################################")
reference=input("Insert only the datset name: ")


df_ref=pd.read_csv("../TP_correction/"+str(reference)+".csv", delimiter=";")
print("#################################################################################################################")
print("CSV file columns: ")
col_ref=df_ref.columns
print(col_ref)
print("#################################################################################################################")


bins=1000

main=ROOT.TFile("Root_"+str(reference)+"_fakeWarning.root","RECREATE")
#plot the histogram and scatter of reference and anal dataset
main.mkdir("plots")
main.cd("plots")

time_ref=np.arange(0,len(df_ref[col_ref[0]]))
etime_ref=1E-20*np.ones(len(df_ref[col_ref[0]]))
ref_gain=nparr(df_ref[col_ref[0]])
err_ref_gain=nparr(df_ref[col_ref[1]])

plot_ref=grapherr(time_ref, df_ref[col_ref[0]], etime_ref, df_ref[col_ref[1]], "Time (a.u.)", "Corrected gain Reference" , 4, 22)
hist_ref=hist(df_ref[col_ref[0]], "Corrected gain reference", bins, 4)

#scale the histogram
hist_ref.Scale(1./hist_ref.Integral())
hist_ref.Write()

#associate frequencies to each histogram bin
xk=np.empty(bins)
pk=np.empty(bins)
for i in range(bins):
    pk[i]=hist_ref.GetBinContent(i)
    xk[i]=hist_ref.GetBinCenter(i)

#normalize the proabbilities
pk_norm = tuple(p/sum(pk) for p in pk)
#create the function where to extract
custm = stats.rv_discrete(name='custm', values=(xk, pk_norm))


#test for extraction
R = custm.rvs(size=1000)
hist_try= ROOT.TH1D("Extracted values","Extracted values;Effective Gas Gain; Entries", bins, 0.9*np.min(ref_gain), 1.1*np.max(ref_gain))
fill_h(hist_try, R)
hist_try.Write()



#running the scan
#we produce 1 file per threshold

#functions
def t_test(mu, sigma, set):
    num=np.abs(np.mean(set)-mu)
    den=np.sqrt(np.square(np.std(set))+np.square(sigma))
    return num/den

def extraction(set):
    exit_set=np.roll(set, -1)
    exit_set[-1]=custm.rvs(size=1)
    return exit_set
#starting set
set= custm.rvs(size=10)


mu=np.mean(ref_gain)
sigma=np.std(ref_gain)



threshold=np.arange(1.5,1.8,0.1)
probability=np.empty(len(threshold))
err_prob=np.empty(len(threshold))

points=2

for i in range(len(threshold)):
    over_thresold=0
    generated=0
    print("##############################")
    print("Threshold is ", threshold[i])
    print("##############################")

    #while over_thresold==0:
    while over_thresold<=points:
        file="output_temp_files/"+str(threshold[i])+".csv"


        generated=generated+1

        if generated%100000000==0:
            print("\t Iteration number: ", generated)
            #print("\t over_thresold: ", over_thresold)

        set=extraction(set)
        t=t_test(mu,sigma,set)
        #print(t)
        if t>threshold[i]:
            over_thresold=over_thresold+1



    probability[i]=over_thresold/generated
    err_prob[i]=np.sqrt( ( probability[i] * (1-probability[i]) ) /generated )

    print("Probability is: ", probability[i], "+/-", err_prob[i])

    np.savetxt(file, nparr([threshold[i], probability[i], err_prob[i]]), newline=';')   # X is an array
































#
#
#
#
#
#
