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
    can1.SaveAs(y_name+" vs "+x_name+".png")
    return can1



f = open("anal_parameters.csv", "r")
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

f = open("../Gain_FIT/fit_parameters.csv", "r")
print("I############################################################")
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
print("         Chose the dataset to analyze ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../Script_downloadAggregate/*.csv")
print("#################################################################################################################")
input=input("Insert only the datset name: ")

df=pd.read_csv("../Script_downloadAggregate/"+str(input)+".csv", delimiter=";")

print("#################################################################################################################")
print("CSV file columns: ")
col=df.columns
print(col)
print("#################################################################################################################")


main=ROOT.TFile("root_"+str(input)+".root","RECREATE")

time_all=np.arange(0,len(df[col[0]]))
etime_all=1E-20*np.ones(len(df[col[0]]))

############################################################################################
main.mkdir("Entry Variables")
main.cd("Entry Variables")
#varieables with errorrs
for i in (3,5,7):
    grapherr(time_all, df[col[i]], etime_all, df[col[i+1]], "Time (a.u.)", col[i] )
#variables without errors
for i in (9,10,11,12,13,14,17,18,19,20,21):
    graph(time_all, df[col[i]], "Time (a.u.)", col[i] )
#bonus
graph(time_all, df["T"]/df["P"], "Time (a.u.)", "T/P" )
############################################################################################

############################################################################################
main.mkdir("Gain vs other variables")
main.cd("Gain vs other variables")

for i in (9,10,11,12,13,14,17,18,19,20, 21):
    grapherr(df[col[i]], df["Gain"], etime_all, df["err gain"],   col[i], "Gain" )
#bonus
grapherr(df["T"]/df["P"],df["Gain"], etime_all, df["err gain"], "T/P", "Gain" )
############################################################################################

############################################################################################
#graph of the gain vs T and P
main.cd()
gtp=ROOT.TGraph2D(len(df["T"]), nparr(df["T"]),nparr(df["P"]), nparr(df["Gain"]));
gtp.GetXaxis().SetTitle("Temperature")
gtp.GetYaxis().SetTitle("Pressure")
gtp.GetXaxis().SetTitle("Gain")
gtp.Write()
############################################################################################


############################################################################################
"""def chi2func(Gi,dGi,a,b,pi,ti):
    chiq=np.empty([len(Gi),int(points)])
    model=np.empty([len(Gi),int(points)])

    model=A*np.exp(B*V*((P0/pi)**a)*((ti/T0)**b))

    print(B*V*((P0/pi)**0.4)*((ti/T0)**0.4))

    chiq=np.sum( np.square(Gi-model)/dGi, axis=1    )
    return chiq/(len(Gi)-2)"""

def chi2func(Gi,dGi,a,b,pi,ti):

    chiq=np.empty([len(Gi),int(points)])
    model=np.empty([len(Gi),int(points)])

    model=A*np.exp(B*V*((P0/pi)**a)*((ti/T0)**b))

    chiq=np.sum( np.square(Gi-model)/dGi, axis=1    )
    return chiq/(len(Gi)-2)


############################################################################################

############################################################################################
#search of the chi2 min
a = np.random.uniform(a_min,a_max,int(points)).reshape((int(points),1))
b = np.random.uniform(b_min,b_max,int(points)).reshape((int(points),1))

chi=chi2func(nparr(df["Gain"]),nparr(df["err gain"]),a,b,nparr(df["P"]),nparr(df["T"]))
#chi[chi > 1E100] = 1E100

print("Minimum of reduced chi2",np.min(chi))
index=np.argmin(chi)
print("a @ min: ", a[index])
print("b @ min: ", b[index])
############################################################################################

############################################################################################
p_err=int(int(points)/10)
#find parameters error
a_err = np.random.uniform(a[index]-1E-4,a[index]+1E-4,p_err).reshape((p_err,1))
b_err = np.random.uniform(b[index]-1E-4,b[index]+1E-4,p_err).reshape((p_err,1))
chi_err=chi2func(nparr(df["Gain"]),nparr(df["err gain"]),a_err,b_err,nparr(df["P"]),nparr(df["T"]))
probable=chi_err[chi_err>chi[index]+1]
#print("int(points) >1 (%): ",(len(probable)/p_err)*100)

print("chi2+1 @ err: ",np.min(chi_err))
index_err=np.argmin(chi_err)
err_a=abs(a_err[index_err]-a[index])
err_b=abs(b_err[index_err]-b[index])
print("err_a @ min: ", err_a)
print("err_b @ min: ", err_b)
############################################################################################

############################################################################################
can1=ROOT.TCanvas("Chi2 values","Chi2 values", 1000, 1000)
can1.SetFillColor(0);
can1.SetBorderMode(0);
can1.SetBorderSize(2);
can1.SetLeftMargin(0.15);
can1.SetRightMargin(0.2);
can1.SetTopMargin(0.1);
can1.SetBottomMargin(0.1);
can1.SetFrameBorderMode(0);
can1.SetFrameBorderMode(0);
can1.SetFixedAspectRatio();

g2_1=ROOT.TGraph2D("","",len(a), a,b,chi);
g2_1.Draw("colz")

can1.Update()

g2_1.GetXaxis().SetTitle("Parameter a")
g2_1.GetYaxis().SetTitle("Parameter b")
g2_1.GetZaxis().SetTitle("#chi^{2}/ndf")



#can1.SetLogz()
can1.Write()

pt1  = ROOT.TPaveText(0.65,0.8,0.8,0.95,"br");
pt1.AddText("a*= "+str('{:.3f}'.format(a[index][0]))+" #pm "+str('{:.3f}'.format(err_a[0])));
pt1.AddText("b*= "+str('{:.3f}'.format(b[index][0]))+" #pm "+str('{:.3f}'.format(err_b[0])));
pt1.AddText("#chi^{2}*/NDF= "+str('{:.2f}'.format(chi[index])));
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

can1.SaveAs("./output_plots/chi2"+input+".png")
can1.SaveAs("./output_plots/chi2"+input+".pdf")
############################################################################################




############################################################################################
f = open("results_"+input+".csv", "w")
f.write("ndf;"+str(len(df["Gain"])-2)+"\n")
f.write("reduced_chi;"+str(chi[index])+"\n")
f.write("a;"+str(a[index][0])+"\n")
f.write("e_a;"+str(err_a[0])+"\n")
f.write("b;"+str(b[index][0])+"\n")
f.write("e_b;"+str(err_b[0])+"\n")

f.close()

############################################################################################

























#
#
#
#
#
#
