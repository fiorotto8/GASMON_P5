import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m
import datetime
import os
import argparse

ROOT.gROOT.SetBatch(True)

if not os.path.exists("output_files"):
    os.makedirs("output_files")

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--delay", help="set delay in points (1 point=30s) from the set date of the percentage and where start to take good data",default=120)
parser.add_argument("-m", "--method", help="Set the correction metod: m or f",default=None)
args = parser.parse_args()

main=ROOT.TFile("analysis_percentage.root","RECREATE")#root file creation

#exponential function
Exponential=ROOT.TF1("Exponential","[0]*exp([1]*x)",20, 40)
Exponential.SetParNames("Constant","Slope")
Exponential.SetParameters(15.53,-0.1883)

#delay in points (1 point = 1/2 minute = 30 sec)
delay=int(args.delay)
#fixed flux of gas
flux=3

def date_to_string(date):
    return str(date.strftime("%Y-%m-%d_%H:%M:%S"))

def string_to_date(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d_%H:%M:%S')

def nearest_index(items, pivot):
    for i in range(len(items)):
        if abs(items[i]-pivot)<datetime.timedelta(seconds=30):
            return i

def ar_error(ar_perc):
    phi_a=(ar_perc*flux)/100
    phi_c=((100-ar_perc)*flux)/100

    dphi_a=2E-3*phi_a+1.2E-2
    dphi_c=2E-3*phi_c+6E-3

    dphi_T=m.sqrt(dphi_a**2+dphi_c**2)

    return ar_perc*m.sqrt( (dphi_T/flux)**2 + (dphi_a/phi_a)**2 )

def c_error(c_perc):
    phi_a=((100-c_perc)*flux)/100
    phi_c=(c_perc*flux)/100

    dphi_a=2E-3*phi_a+1.2E-2
    dphi_c=2E-3*phi_c+6E-3

    dphi_T=m.sqrt(dphi_a**2+dphi_c**2)

    return c_perc*m.sqrt( (dphi_T/flux)**2 + (dphi_c/phi_c)**2 )

def nparr(list):
    return np.array(list, dtype="d")

#define filling histogram function
def fill_h(histo_name, array):
    for x in range (len(array)):
        histo_name.Fill((np.array(array[x] ,dtype="d")))





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
#
#
#
#1) import all the data needed
#2) defining correction function, apply the correction on all the dataset and store it
    #2.1)store .csv
    #2.2)store scatter canvas in root file
    #2.3)store histogram canvas in root file
#3)Individuate the data interval relative to the selected percentage
    #3.1)Plot histogram of these gains
    #3.2)Plot scatter of these gains
    #3.3) Store average gain and errors @ this ar and co2 percentage
    #3.4) plot G vs % and fit it
#
#
#
#check if folder exist, if not create it
if not os.path.isdir("output_files"):
    os.makedirs("output_files")

#1)
print("#################################################################################################################")
print("         Chose the dataset to analyze ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../../Script_downloadAggregate/*.csv")
print("#################################################################################################################")
inputdf=input("Insert only the datset name: ")

dataset=pd.read_csv("../../Script_downloadAggregate/"+str(inputdf)+".csv", delimiter=";")

rate=rate_calc(dataset["Timestamp"],r0,folder)
print(rate)
gain=-1*nparr(dataset["Mean Current"])/(200*1.6E-19*rate)
err_gain=nparr(dataset["Mean Error"])/(200*1.6E-19*rate)

V=np.mean(nparr(dataset["Vmon"]))
G0=A*m.exp(B*V)
print("V=",V,"G0=",G0)

#import timing and percentages
timing_string="./timing_percentage.txt"
timing_col=["Change Time",	"CO2 Percentage"]
timing =  pd.read_csv(  timing_string  ,   usecols=timing_col ,  delimiter=";"  )

#import correction parameters
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
    os.system("ls -lrt ../../StepAnalysis/TP_Fit/*.csv")
    print("#################################################################################################################")
    correction_par=input("Insert only the datset name: ")
    f = open("../../StepAnalysis/TP_Fit/"+correction_par+".csv", "r")
elif method=="m":
    print("#################################################################################################################")
    print("         Choose the analysis results to use ")
    print("Copy/Paste one name from the following list, if it is not present you should generate the correction")
    print("IF YOU ARE SURE THE CORRETION HAS BEEN CREATED WITH THE SAME NAME AS THE ORIGNAL DATASETAND NO OTHER STRANGE NAMES HAS BEEN USED TYPE : same")
    print("#################################################################################################################")
    os.system("ls -lrt ../../StepAnalysis/MiniminzingVariance/*.csv")
    print("#################################################################################################################")
    correction_par=input("Insert only the datset name: ")
    f = open("../../StepAnalysis/MiniminzingVariance/"+correction_par+".csv", "r")
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

"""
correction_string="./results_output.csv"
correction_col=["a @ min","err a",   "b @ min","err b" ,"A", "B"]
correction =  pd.read_csv(  correction_string  ,   usecols=correction_col ,  delimiter=";"  )
"""

points=np.array([x for x in range(len(dataset["Mean Current"]))],dtype="d"  )


#2)

def correction(G,err_G,t,p):
    """
    a=-0.64918376
    b=-0.0561216
    P0=100910.3801	#Pa
    T0=18.7063261	#C
    """
    G=nparr(G)
    err_G=nparr(err_G)

    t=nparr(t)
    p=nparr(p)

    X=G**(  (P0/p)**(-a)  *  (t/T0)**(-b)   )
    #Y= A**   (  (P0/p)**(a)  *  (t/T0)**(b)    )
    Y= A**   (  (P0/p)**(-a)  *  (t/T0)**(-b)        -1)
    #Y=1
    corr=X/Y

    X=(P0/p)**(-a)
    Y=(t/T0)**(-b)

    error=   (A**(1-X*Y)) * (G**(X*Y)) * X * Y * np.sqrt( np.square(err_G/G) +      np.square( e_a*np.log(P0/p)*(np.log(A)-np.log(G)) ) + np.square( (np.log(A)-np.log(G))*e_b*np.log(t/T0) )     )

    return np.array([corr,error], dtype="d")

#2.1)
#you can test the output
#print(correction(dataset["Mean Current"],dataset["Mean Error"], dataset["T"], dataset["P"]))
corr_gain_w_err=correction(gain,err_gain, dataset["T"], dataset["P"])

#create DataFrame
corr_gain=pd.DataFrame( { "Timestamp":dataset["Timestamp"], "gain corr": corr_gain_w_err[0], "err gain corr": corr_gain_w_err[1]   } )
#write dataframe
corr_gain.to_csv("output_files/CorrectedDataset.csv", sep=';', header=True, index=False, mode='w')


#au time
time=np.array([x for x in range(len(dataset["Timestamp"]))],dtype="d")
err_time=np.array([1E-5 for x in range(len(dataset["Timestamp"]))],dtype="d")


#2.2)
#corrected not corrected comparison
c_scatter= ROOT.TCanvas("Gain comparison Scatter", "Gain comparison Scatter",0,0, 800,800)
c_scatter.SetFillColor(0);
c_scatter.SetBorderMode(0);
c_scatter.SetBorderSize(2);
c_scatter.SetLeftMargin(0.17);
c_scatter.SetRightMargin(0.040201);
c_scatter.SetTopMargin(0.01);
c_scatter.SetBottomMargin(0.1);
c_scatter.SetFrameBorderMode(0);
c_scatter.SetFrameBorderMode(0);
c_scatter.SetFixedAspectRatio();

mg=ROOT.TMultiGraph()

plotB = ROOT.TGraphErrors(len(time),  time, nparr(gain), err_time, nparr(err_gain)      )
plotB.SetMarkerColor(4)#blue
plotB.SetMarkerStyle(22)
plotB.SetMarkerSize(1)
plotB.SetDrawOption("C");#smooth curve
mg.Add(plotB)

plotA = ROOT.TGraphErrors(len(time),  time, corr_gain_w_err[0], err_time, corr_gain_w_err[1]      )
plotA.SetMarkerColor(3)#green
plotA.SetMarkerStyle(22)
plotA.SetMarkerSize(1)
plotA.SetDrawOption("C");#smooth curve
mg.Add(plotA)

mg.Draw("AP")

leg = ROOT.TLegend(0.6663327,0.1303901,0.9519038,0.2710472);
#leg.SetHeader("The Legend Title");
leg.AddEntry(plotB,"BEFORE");
leg.AddEntry(plotA,"AFTER");

leg.Draw("SAME");
mg.GetYaxis().SetTitle("Effective Gas gain")
mg.GetXaxis().SetTitle("Time(a.u.)")
c_scatter.Update()
c_scatter.Write()


#2.3)
#corrected not corrected comparison
c_histo= ROOT.TCanvas("Gain comparison Histogram", "Gain comparison Histogram",0,0, 800,800)
c_histo.SetFillColor(0);
c_histo.SetBorderMode(0);
c_histo.SetBorderSize(2);
c_histo.SetLeftMargin(0.17);
c_histo.SetRightMargin(0.040201);
c_histo.SetTopMargin(0.01);
c_histo.SetBottomMargin(0.1);
c_histo.SetFrameBorderMode(0);
c_histo.SetFrameBorderMode(0);
c_histo.SetFixedAspectRatio();
ch=100
min=np.min([0.99*np.min(corr_gain_w_err[0]), 0.99*np.min(nparr(gain))])
max=np.max([1.01*np.max(corr_gain_w_err[0]), 1.01*np.max(nparr(gain))])






histoA= ROOT.TH1D(""," ;Effective Gas Gain; Entries", ch*10, min, max)
fill_h(histoA, corr_gain_w_err[0])
histoA.SetLineColor(3)
histoA.Draw()

#temp=-1*np.array(dataset["Mean Current"],dtype="d")/(n0*e*rate)
histoB= ROOT.TH1D(""," ;Effective Gas Gain; Entries", ch*10, min, max)
fill_h(histoB, nparr(gain))
histoB.SetLineColor(4)
histoB.Draw("SAME")



leg = ROOT.TLegend(0.6663327,0.1303901,0.9519038,0.2710472);
#leg.SetHeader("The Legend Title");
leg.AddEntry(histoA,"AFTER");
leg.AddEntry(histoB,"BEFORE");

leg.Draw("SAME");
c_histo.Update()
c_histo.Write()




error_perc=corr_gain_w_err[1]/corr_gain_w_err[0]

#print(error_perc)

hh= ROOT.TH1D("Percentual error on Corrected Gain","Percentual error on Corrected Gain;Percentual error corrected gain; Entries", ch*10, 0.9*np.min(error_perc), 1.1*np.max(error_perc))
fill_h(hh, error_perc)
hh.SetLineColor(3)
hh.Write()


#3)
timestamp_date=[string_to_date(dataset["Timestamp"][x]) for x in range(len(dataset["Timestamp"]))]

Gc_percentage=np.empty(len(timing["Change Time"]))
e_Gc_percentage=np.empty(len(timing["Change Time"]))

#Gaus function
Gaus=ROOT.TF1("Gaus","gaus(0)",20, 40)
Gaus.SetParNames("Constant","Mean", "Sigma")

chi2gaus=np.zeros(len(timing["Change Time"]))

for j in range(len(timing["Change Time"])):
    main.cd()
    main.mkdir(str(timing["CO2 Percentage"][j])+" % CO2 data")
    main.cd(str(timing["CO2 Percentage"][j])+" % CO2 data")

    if  j!=(len(timing["Change Time"])-1) and (string_to_date(timing["Change Time"][j])+datetime.timedelta(minutes=delay/2))>string_to_date(timing["Change Time"][j+1]):
        print("ERROR")
        print("The time difference between two consectuive timestamp entries in timing_percentage.csv is higher than the set delay time")
        print("This involves in the "+str(j+2)+"th and "+str(j+3)+"th lines in the .csv")
        print("j is equal to "+str(j)+" in the cycle")
        break

    if  j!=(len(timing["Change Time"])-1):
        min_edge=string_to_date(timing["Change Time"][j])+datetime.timedelta(minutes=delay/2)
        max_edge=string_to_date(timing["Change Time"][j+1])

    else:
        min_edge=string_to_date(timing["Change Time"][j])+datetime.timedelta(minutes=delay/2)
        max_edge=string_to_date(dataset["Timestamp"].iloc[-1])



    print("Index edges for "+str(timing["CO2 Percentage"][j])+"% CO2: ",nearest_index(timestamp_date,min_edge),nearest_index(timestamp_date,max_edge))

    time_cut=time[nearest_index(timestamp_date,min_edge):nearest_index(timestamp_date,max_edge)]
    e_time_cut=err_time[nearest_index(timestamp_date,min_edge):nearest_index(timestamp_date,max_edge)]
    Gc_cut=corr_gain_w_err[0][nearest_index(timestamp_date,min_edge):nearest_index(timestamp_date,max_edge)]
    e_Gc_cut=corr_gain_w_err[1][nearest_index(timestamp_date,min_edge):nearest_index(timestamp_date,max_edge)]

    #print(type(time_cut), type(e_time_cut), type(Gc_cut), type(e_Gc_cut))

    #3.1)
    histo= ROOT.TH1D("Histogram Gain @ "+str(timing["CO2 Percentage"][j])+"% CO2: ","Histogram Gain @ "+str(timing["CO2 Percentage"][j])+"% CO2:  ;Effective Gas Gain; Entries", ch, 0.9*np.min(Gc_cut), 1.1*np.max(Gc_cut))
    fill_h(histo, Gc_cut)
    histo.Fit("Gaus","RQ","", 0.9*np.min(Gc_cut), 1.1*np.max(Gc_cut))
    chi2gaus[j]=Gaus.GetChisquare()/Gaus.GetNDF()
    if chi2gaus[j]>3:
        print("Fit of "+str(timing["CO2 Percentage"][j])+" % CO2 is not very good (chi2/NDF>3)")

    histo.Write()

    #3.2)
    plot = ROOT.TGraphErrors(len(time_cut),  time_cut, Gc_cut, e_time_cut, e_Gc_cut      )
    plot.SetName("Scatter Gain @ "+str(timing["CO2 Percentage"][j])+"% CO2: ")
    plot.SetTitle("Scatter Gain @ "+str(timing["CO2 Percentage"][j])+"% CO2: ")
    plot.GetXaxis().SetTitle("Time (a.u.)")
    plot.GetYaxis().SetTitle("Effective Gas Gain")
    plot.SetMarkerColor(4)#blue
    plot.SetMarkerStyle(22)
    plot.SetMarkerSize(1)
    plot.SetDrawOption("C");#smooth curve


    plot.Write()

    #3.3)
    Gc_percentage[j]=histo.GetMean()
    e_Gc_percentage[j]=histo.GetStdDev()/m.sqrt(len(time_cut))


perc_A=np.empty(len(timing["CO2 Percentage"]))
e_perc_A=np.empty(len(timing["CO2 Percentage"]))
perc_C=np.empty(len(timing["CO2 Percentage"]))
e_perc_C=np.empty(len(timing["CO2 Percentage"]))

for h in range(len(timing["CO2 Percentage"])):
    perc_A[h]=100-timing["CO2 Percentage"][h]
    e_perc_A[h]=ar_error(perc_A[h])
    perc_C[h]=timing["CO2 Percentage"][h]
    e_perc_C[h]=c_error(perc_C[h])


#print(perc_A, e_perc_A,perc_C, e_perc_C)

#create DataFrame
corr_gain=pd.DataFrame( { "CO2 %":perc_C, "CO2 % err": e_perc_C,"Ar %":perc_A, "Ar % err": e_perc_A, "mean gain":Gc_percentage, "err gain": e_Gc_percentage   } )
#write dataframe
corr_gain.to_csv("output_files/gainVSpercentage.csv", sep=';', header=True, index=False, mode='w')



main.cd()

histo= ROOT.TH1D("Histogram of gaus chi2","Histogram of gaus chi2", 15, 0.9*np.min(chi2gaus), 1.1*np.max(chi2gaus))
fill_h(histo, chi2gaus)
histo.Write()




plot = ROOT.TGraphErrors(len(perc_A),  perc_A, Gc_percentage, e_perc_A, e_Gc_percentage      )
plot.SetName("Gain as a function of the Argon percentage")
plot.SetTitle("Gain as a function of the Argon percentage")
plot.GetXaxis().SetTitle("Argon percentage (%)")
plot.GetYaxis().SetTitle("Effective Gas Gain")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.SetDrawOption("C");#smooth curve
Exponential.SetParameters(0.02, 0.2)
plot.Fit("Exponential","RQ"," ",60,80)
plot.Write()


c_co2= ROOT.TCanvas("Gain vs CO_{2} percentage", "Gain vs CO_{2} percentage",0,0, 800,800)
c_co2.SetLeftMargin(0.15);
c_co2.SetRightMargin(0.02);
c_co2.SetFixedAspectRatio()
c_co2.SetTopMargin(0.015)

plot = ROOT.TGraphErrors(len(perc_C),  perc_C, Gc_percentage, e_perc_C, e_Gc_percentage      )
plot.SetTitle("")
plot.GetXaxis().SetTitle("CO_{2} percentage (%)")
plot.GetYaxis().SetTitle("Effective Gas Gain")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.GetYaxis().SetDecimals(0)
Exponential.SetParameters(6.6E6, -0.2)
plot.Fit("Exponential","RQ","R")
plot.Write()

plot.Draw("AP")

pt1  = ROOT.TPaveText(0.6,0.8,0.9,0.9,"NDC");
pt1.AddText("A= "+str('{:.3e}'.format(Exponential.GetParameter(0)))+" +/- "+str('{:.3e}'.format(Exponential.GetParError(0))));
pt1.AddText("#mu= "+str('{:.3f}'.format(Exponential.GetParameter(1)))+" +/- "+str('{:.3f}'.format(Exponential.GetParError(1))));
pt1.AddText("#chi^{2}/NDF= "+str('{:.2f}'.format(Exponential.GetChisquare()/Exponential.GetNDF())));

pt1.SetBorderSize(0);
pt1.SetLineColor(1);
pt1.SetLineStyle(1);
pt1.SetLineWidth(2);
pt1.SetFillColor(0);
pt1.SetFillStyle(1001);
pt1.SetTextSize(0.03);
pt1.SetTextFont(42);
pt1.SetTextAlign(11);
pt1.SetFillStyle(3050);
pt1.Draw("SAME")

c_co2.SaveAs("output_files/GainCO2.png")
c_co2.SaveAs("output_files/GainCO2.pdf")






































#
#
#
#
#
#
