import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m
import datetime
import tqdm
import uproot
import sys
import os
from array import array
import argparse

if not os.path.exists("output_plots"):
    os.makedirs("output_plots")

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="set the name of the dataset",default=None)
parser.add_argument("-m", "--method", help="Set the correction metod: m or f",default=None)
args = parser.parse_args()

def rate_calc(timestamp,r0,start):
#Calculate the hit rate of 55Fe source starting from a r0 measured @ start_date with second precision
#wite the date in %Y-%m-%d_%H:%M:%S format
#decay time is 1452.36 days or 12.55E9 seconds
#NB -> timestamp has to be a list also if it is one-sized
    def string_to_date(string):
        return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')

    start_date=start+'_12:00:00'

    #r0=300
    tau=1.255E8#seconds

    rate=np.empty(len(timestamp))

    for i in range(len(timestamp)):
        dt=(string_to_date(timestamp[i])-string_to_date(start_date)).total_seconds()
        rate[i]=r0*m.exp(-dt/tau)

    return rate

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
    #can1.SaveAs(y_name+" vs "+x_name+".png")
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

f = open("../TP_Fit/anal_parameters.txt", "r")
print("I############################################################")
print("Input parameters are:")
#the input parametrs are declared as variebales as they are neamed in the anal_parameters.csv file
for x in f:
    a=x.split(";",1)
    var=a[0]
    b=a[1].split("\n",1)
    val=float(b[0])
    print("#",var, "=", val)
    exec(var+"="+str(val))
f.close()

print("#################################################################################################################")
print("         Chose the Gain measurement to use ")
print("Copy/Paste one FOLDER name")
print("#################################################################################################################")
os.system("ls -lrt ../../Gain_FIT")
print("#################################################################################################################")
folder=input("Insert only the FOLDER name: ")


f = open("../../Gain_FIT/"+str(folder)+"/fit_parameters.txt", "r")
print("############################################################")
print("Gain Fit parameters are:")
#the input parametrs are declared as variebales as they are neamed in the anal_parameters.csv file
for x in f:
    a=x.split(";",1)
    var=a[0]
    b=a[1].split("\n",1)
    val=float(b[0])
    print("#",var, "=", val)
    exec(var+"="+str(val))
f.close()


print("#################################################################################################################")
print("         Chose the dataset to correct ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../../Script_downloadAggregate/*.csv")
print("#################################################################################################################")
to_corr=input("Insert only the datset name: ")
#to_corr="Dataset_2021-09-22_2021-10-20"


if args.method is None:
    print("Use Minizer or Fit results??")
    method=input("m/f?")
else: method=args.method

if method=="f":
    print("#################################################################################################################")
    print("         Choose the analysis results to use ")
    print("Copy/Paste one name from the following list, if it is not present you should generate the correction")
    print("IF YOU ARE SURE THE CORRETION HAS BEEN CREATED WITH THE SAME NAME AS THE ORIGNAL DATASETAND NO OTHER STRANGE NAMES HAS BEEN USED TYPE : same")
    print("#################################################################################################################")
    os.system("ls -lrt ../TP_Fit/*.csv")
    print("#################################################################################################################")
    correction_par=input("Insert only the datset name: ")
    if correction_par=="same": f = open("../TP_Fit/results_"+to_corr+".csv", "r")
    else: f = open("../TP_Fit/"+correction_par+".csv", "r")
elif method=="m":
    print("#################################################################################################################")
    print("         Choose the analysis results to use ")
    print("Copy/Paste one name from the following list, if it is not present you should generate the correction")
    print("IF YOU ARE SURE THE CORRETION HAS BEEN CREATED WITH THE SAME NAME AS THE ORIGNAL DATASETAND NO OTHER STRANGE NAMES HAS BEEN USED TYPE : same")
    print("#################################################################################################################")
    os.system("ls -lrt ../MiniminzingVariance/*.csv")
    print("#################################################################################################################")
    correction_par=input("Insert only the datset name: ")
    if correction_par=="same": f = open("../MiniminzingVariance/results_"+to_corr+".csv", "r")
    else: f = open("../MiniminzingVariance/"+correction_par+".csv", "r")
else: print("You inserted the wrong letter my friend ;)")

print("############################################################")
print("TP parameters are:")
#the input parametrs are declared as variebales as they are neamed in the anal_parameters.csv file
for x in f:
    k=x.split(";",1)
    var=k[0]
    j=k[1].split("\n",1)
    val=float(j[0])
    print("#",var, "=", val)
    exec(var+"="+str(val))
f.close()

df=pd.read_csv("../../Script_downloadAggregate/"+str(to_corr)+".csv", delimiter=";")

print("#################################################################################################################")
print("CSV file columns: ")
col=df.columns
print(col)
print("#################################################################################################################")

rate=rate_calc(df["Timestamp"],r0,folder)
print(rate)
gain=-1*nparr(df["Mean Current"])/(200*1.6E-19*rate)
err_gain=nparr(df["Mean Error"])/(200*1.6E-19*rate)


############################################################################################

def correction(G,err_G,t,p):
    G=nparr(G)
    err_G=nparr(err_G)
    t=nparr(t)
    p=nparr(p)

    X=G**(  (P0/p)**(-a)  *  (t/T0)**(-b)   )
    Y= A**   (  (P0/p)**(-a)  *  (t/T0)**(-b)        -1)
    corr=X/Y

    X=(P0/p)**(-a)
    Y=(t/T0)**(-b)
    error=   (A**(1-X*Y)) * (G**(X*Y)) * X * Y * np.sqrt( np.square(err_G/G) +      np.square( e_a*np.log(P0/p)*(np.log(A)-np.log(G)) ) + np.square( (np.log(A)-np.log(G))*e_b*np.log(t/T0) )     )

    return [corr, error]

if args.name is None: main=ROOT.TFile(str(to_corr)+"_corrected_with_"+str(correction_par)+".root","RECREATE")
else: main=ROOT.TFile(args.name+".root","RECREATE")


############################################################################################

time_all=np.arange(0,len(df[col[0]]))
etime_all=1E-20*np.ones(len(df[col[0]]))

plot_nocorr=grapherr(time_all, gain, etime_all, err_gain, "Time (a.u.)", "Gain before correction" , 4, 22)
hist_nocorr=hist(gain, "Gain before correction", 1000, 4)

corrz=correction(gain, err_gain, df["T"], df["P"])

plot_corr=grapherr(time_all, corrz[0], etime_all, corrz[1], "Time (a.u.)", "Gain after correction" , 2, 23)
hist_corr=hist(corrz[0], "Gain after correction", 1000, 2)

################################################################################################

g_max=np.max([1.01*np.max(nparr(gain)),1.01*np.max(corrz[0]) ])
g_min=np.min([0.99*np.min(nparr(gain)),0.99*np.min(corrz[0])])
#print(g_min, g_max)

################################################################################################
cv_histo= ROOT.TCanvas("cv_histo", " ",0,0, 1000,1000)
cv_histo.SetFillColor(0);
cv_histo.SetBorderMode(0);
cv_histo.SetBorderSize(2);
cv_histo.SetLeftMargin(0.12);
cv_histo.SetRightMargin(0.08);
cv_histo.SetTopMargin(0.1);
cv_histo.SetBottomMargin(0.1);
cv_histo.SetFrameBorderMode(0);
cv_histo.SetFrameBorderMode(0);
cv_histo.SetFixedAspectRatio();

hist_nocorr.Draw()
hist_corr.Draw("SAME")

cv_histo.Update()

leg = ROOT.TLegend(0.1603206,0.7330595,0.4709419,0.8829569);
#leg.SetHeader("The Legend Title");
leg.AddEntry(hist_nocorr,"Measured Gain");
leg.AddEntry(hist_corr,"Corrected Gain");
leg.Draw("SAME");

cv_histo.Update()

cv_histo.Write()

cv_histo.SaveAs("./output_plots/"+"Corrected_"+str(to_corr)+"_with_"+str(correction_par)+"GasGain-histo_selected.png");
cv_histo.SaveAs("./output_plots/"+"Corrected_"+str(to_corr)+"_with_"+str(correction_par)+"GasGain-histo_selected.pdf");

###########################################################################


###########################################################################

cv_scat= ROOT.TCanvas("cv_scat", " ",0,0, 1000,1000)
cv_scat.SetFillColor(0);
cv_scat.SetBorderMode(0);
cv_scat.SetBorderSize(2);
cv_scat.SetLeftMargin(0.15);
cv_scat.SetRightMargin(0.08);
cv_scat.SetTopMargin(0.1);
cv_scat.SetBottomMargin(0.1);
cv_scat.SetFrameBorderMode(0);
cv_scat.SetFrameBorderMode(0);
cv_scat.SetFixedAspectRatio();

mg=ROOT.TMultiGraph()
mg.Add(plot_nocorr)
mg.Add(plot_corr)

mg.GetYaxis().SetTitle("Effective Gas gain")
mg.GetXaxis().SetTitle("Time (a.u.)")
mg.GetXaxis().SetMaxDigits(3);
mg.GetXaxis().SetDecimals();
mg.GetYaxis().SetLimits(g_min,g_max);

mg.Draw("AP")

cv_scat.Update()

leg = ROOT.TLegend(0.1472946,0.1273101,0.4579158,0.2772074);
#leg.SetHeader("The Legend Title");
leg.AddEntry(hist_nocorr,"Measured Gain");
leg.AddEntry(hist_corr,"Corrected Gain");

leg.Draw("SAME");

cv_scat.Update()

cv_scat.Write()

if args.name is None:
    cv_scat.SaveAs("./output_plots/"+"Corrected_"+str(to_corr)+"_with_"+str(correction_par)+"GasGain-scatter_selected.png");
    cv_scat.SaveAs("./output_plots/"+"Corrected_"+str(to_corr)+"_with_"+str(correction_par)+"GasGain-scatter_selected.pdf");
else:
    cv_scat.SaveAs("./output_plots/"+args.name+"_GasGain-scatter_selected.png");
    cv_scat.SaveAs("./output_plots/"+args.name+"_GasGain-scatter_selected.pdf");

#################################################################################################


#create DataFrame
dt=pd.DataFrame( { "Corrected Gain":corrz[0], "err Gain": corrz[1]   } )
#write dataframe
if args.name is None: dt.to_csv("Corrected_"+str(to_corr)+"_with_"+str(correction_par)+".csv", sep=';', header=True, index=False, mode='w')
else: dt.to_csv(args.name+".csv", sep=';', header=True, index=False, mode='w')



























#
#
#
#
#
#
