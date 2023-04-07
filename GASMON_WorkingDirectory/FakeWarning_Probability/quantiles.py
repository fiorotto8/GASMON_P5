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
        plot.SetLineColor(color)#blue
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

def canvas(plot, size=800, leftmargin=0.1, rightmargin=0.2, log=0):
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

    if log==1:
        can1.SetLogy()


    can1.Write()
    can1.SaveAs(y_name+" vs "+x_name+".png")
    return can1

def hist(list, x_name, channels=100, linecolor=4, linewidth=4):
    def fill_h(histo_name, array):
        for x in range (len(array)):
            histo_name.Fill((np.array(array[x] ,dtype="d")))

    array=np.array(list ,dtype="d")

    hist=ROOT.TH1D(x_name,x_name,channels,0.99*np.min(array),1.01*np.max(array))
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
os.system("ls -lrt ../Script_downloadAggregate/*.csv")
print("#################################################################################################################")
reference=input("Insert only the datset name: ")


df_ref=pd.read_csv("../Script_downloadAggregate/"+str(reference)+".csv", delimiter=";")
print("#################################################################################################################")
print("CSV file columns: ")
col_ref=df_ref.columns
print(col_ref)
print("#################################################################################################################")

gaus = ROOT.TF1("gaus","gaus",0,10)

main=ROOT.TFile("Quantiles_"+str(reference)+".root","recreate")

bins=1000

#main=ROOT.TFile("Root_"+str(reference)+"_fakeWarning.root","RECREATE")
#plot the histogram and scatter of reference and anal dataset
main.mkdir("reference plots")
main.cd("reference plots")

time_ref=np.arange(0,len(df_ref["Gain Corrected"]))
etime_ref=1E-20*np.ones(len(df_ref["Gain Corrected"]))
ref_gain=nparr(df_ref["Gain Corrected"])
err_ref_gain=np.zeros(len(ref_gain))

plot_ref=grapherr(time_ref, ref_gain, etime_ref, err_ref_gain, "Time (a.u.)", "Corrected gain Reference" , 4, 22)
hist_ref=hist(ref_gain, "Corrected gain reference", bins, 4)


gaus = ROOT.TF1("gaus","gaus",0.99*np.min(ref_gain),1.01*np.max(ref_gain))

#scale the histogram
hist_ref.Scale(1./hist_ref.Integral())

mean = np.mean(ref_gain)
sigma = np.std(ref_gain)


#t computation
main.cd()
av=10
def tvalue(sample):
    tvalues=np.empty(len(sample)-av)
    for i in range(len(tvalues)):
        temp_m=np.mean(sample[i:i+av])
        temp_s=np.std(sample[i:i+av])

         #print(mean, temp_m, sigma, temp_s)
        tvalues[i]=(mean-temp_m)/(m.sqrt(sigma*sigma+temp_s*temp_s))

    return tvalues


t_ref=tvalue(ref_gain)

plot=graph(time_ref[:-10], t_ref, "Time (a.u.)", "t_values" , 4, 22)
hist=hist(t_ref, "t_values", bins, 4)
hist.Scale(1./hist.Integral())
hist.Write()

#associate frequencies to each histogram bin
xk=np.empty(bins)
pk=np.empty(bins)
for i in range(bins):
    pk[i]=hist.GetBinContent(i)
    xk[i]=hist.GetBinCenter(i)

threshold=np.arange(0,4,0.1)

prob, err_prob=np.zeros(len(threshold)),np.zeros(len(threshold))

for i in range(len(threshold)):
    temp_prob=0
    for j in range(bins):
        if abs(xk[j])>=threshold[i]:
            temp_prob=temp_prob+pk[j]
        else:
            temp_prob=temp_prob
        prob[i]=temp_prob
        err_prob[i]=np.sqrt( ( prob[i] * (1-prob[i]) ) /bins )

#print(err_prob)

plot=grapherr(threshold, prob,1E-20*threshold, err_prob, "Threshold value", "Fake Warning Probability" , 4, 4, 1.5)


cv= ROOT.TCanvas("cv", " ",0,0, 800,800)
cv.SetFillColor(0);
cv.SetBorderMode(0);
cv.SetBorderSize(2);
cv.SetLeftMargin(0.15);
cv.SetRightMargin(0.040201);
cv.SetTopMargin(0.1);
cv.SetBottomMargin(0.1);
cv.SetFrameBorderMode(0);
cv.SetFrameBorderMode(0);
cv.SetFixedAspectRatio();

plot.Draw("AP")

plot.GetYaxis().SetRangeUser(1E-7,2);
#plot.GetXaxis().SetRangeUser(0,1.85);

cv.SetLogy()
cv.Update()


#save as pdf and/or png
cv.SaveAs("output_plots/FakeWarning.png");
cv.SaveAs("output_plots/FakeWarning.pdf");
#ROOT.gApplication.Run()

#create DataFrame
dt=pd.DataFrame( { "thresholds":threshold, "probability": prob, "err probability": err_prob  } )
#write dataframe
dt.to_csv("ThresholdsFrom_"+str(reference)+".csv", sep=';', header=True, index=False, mode='w')














#
#
#
#
#
#
#
