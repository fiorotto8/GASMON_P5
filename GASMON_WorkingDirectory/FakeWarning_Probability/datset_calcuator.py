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

string=sys.argv[1]
points=int(float(string))
main=ROOT.TFile("generated_samples/Sample"+string+".root","recreate")


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
os.system("ls -lrt ../TP_correction/*.csv")
print("#################################################################################################################")
reference=input("Insert only the datset name: ")


df_ref=pd.read_csv("../TP_correction/"+str(reference)+".csv", delimiter=";")
print("#################################################################################################################")
print("CSV file columns: ")
col_ref=df_ref.columns
print(col_ref)
print("#################################################################################################################")

gaus = ROOT.TF1("gaus","gaus",0,10)

bins=1000

#main=ROOT.TFile("Root_"+str(reference)+"_fakeWarning.root","RECREATE")
#plot the histogram and scatter of reference and anal dataset
main.mkdir("reference plots")
main.cd("reference plots")

time_ref=np.arange(0,len(df_ref[col_ref[0]]))
etime_ref=1E-20*np.ones(len(df_ref[col_ref[0]]))
ref_gain=nparr(df_ref[col_ref[0]])
err_ref_gain=nparr(df_ref[col_ref[1]])

plot_ref=grapherr(time_ref, df_ref[col_ref[0]], etime_ref, df_ref[col_ref[1]], "Time (a.u.)", "Corrected gain Reference" , 4, 22)
hist_ref=hist(df_ref[col_ref[0]], "Corrected gain reference", bins, 4)


gaus = ROOT.TF1("gaus","gaus",0.99*np.min(ref_gain),1.01*np.max(ref_gain))

#scale the histogram
hist_ref.Scale(1./hist_ref.Integral())
hist_ref.Fit("gaus", "RQ","r")
hist_ref.Write()

mean = gaus.GetParameter(1)
sigma = gaus.GetParameter(2)

print(mean, sigma)
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


R = custm.rvs(size=points)

histoN= ROOT.TH1D("Extracted values","Extracted values;Effective Gas Gain; Entries", bins, 0.99*np.min(R), 1.01*np.max(R))
fill_h(histoN, R)
#histoN.Write()




data=ROOT.TNtuple("T","Simple NTplue", "population:gaussian")

for i in tqdm.tqdm(range(points)):
    data.Fill( R[i] , np.random.randn(1)*sigma+mean )
data.Write()

main.Close()






















#
#
#
#
