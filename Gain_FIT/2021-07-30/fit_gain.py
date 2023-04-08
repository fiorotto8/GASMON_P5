import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m
import datetime
import tqdm
def nparr(string):
    return np.array(string, dtype="d")

main=ROOT.TFile("result_fit.root","RECREATE")#root file creation

#test on gain_meas
cal_off=1.026
print("Shift is: ", cal_off)

#1)
#fit gain curve
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
#exponential function

#################################
#CALIBRATION OFFSET
#cal_off=1.02
#################################

g=pd.read_csv(  "gain-meas.csv"  ,   usecols=["V","G","err","RatePlat"] ,  delimiter=";"  )

Exponential=ROOT.TF1("Exponential","[0]*exp([1]*x)",min(g["V"]),max(g["V"]))
Exponential.SetParNames("Constant","Slope")
Exponential.SetParameters(1,8E-3)

cv= ROOT.TCanvas("cv", " ",0,0, 800,800)
cv.SetFillColor(0)
cv.SetBorderMode(0)
cv.SetBorderSize(2)
cv.SetLeftMargin(0.18)
cv.SetRightMargin(0.08)
cv.SetTopMargin(0.1)
cv.SetBottomMargin(0.1)
cv.SetFrameBorderMode(0)
cv.SetFrameBorderMode(0)
cv.SetFixedAspectRatio()

plot = ROOT.TGraphErrors(len(g["V"]),  np.array(g["V"]  ,dtype="d")  ,   cal_off*np.array(g["G"]  ,dtype="d") , 1E-9*np.array(   g["err"]   ,dtype="d"),np.array(  g["err"]    ,dtype="d"))
plot.SetTitle("Gain vs Voltage")
plot.SetName("Gain vs Voltage")
plot.GetXaxis().SetTitle("Voltage (V)")
plot.GetYaxis().SetTitle("Gain")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(2)
#plot.SetDrawOption("C");#smooth curve
plot.Fit("Exponential", "RQ","r")
plot.Write()

ROOT.gStyle.SetOptFit()

plot.Draw("AP")

cv.SetLogy()
cv.Update()

cv.SaveAs("gainVSvoltage.pdf")
cv.SaveAs("gainVSvoltage.png")

########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
f = open("env.txt", "r")
T,P=[],[]
for x in f:
    a=x.split(";",1)
    T.append(float(a[0]))
    P.append(float(a[1].split("\n",1)[0]))
f.close()

T=nparr(T)
P=nparr(P)
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################

A=Exponential.GetParameter(0)
eA=Exponential.GetParError(0)
B=Exponential.GetParameter(1)
eB=Exponential.GetParError(1)

f = open("fit_parameters.txt", "w")
f.write("A;"+str(A)+"\n")
f.write("eA;"+str(eA)+"\n")
f.write("B;"+str(B)+"\n")
f.write("eB;"+str(eB)+"\n")
f.write("P0;"+str(np.mean(P))+"\n")
f.write("T0;"+str(np.mean(T))+"\n")
f.write("r0;"+str(g["RatePlat"][0]))

f.close()





########################################################################################################################################################################################################################################################################################################################################################################################################################################################################









#
#
#
#
#
#
