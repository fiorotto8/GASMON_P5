import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m
import datetime
import tqdm

def nparr(list):
    return np.array(list, dtype="d")

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

def hist2D(name,list_x, list_y, x_name, y_name, channels=20, linecolor=4, linewidth=4):
    def fill_h(histo_name, array_x, array_y):
        for x in range (len(array_x)):
            histo_name.Fill(array_x[x],array_y[x])

    array_x, array_y=nparr(list_x), nparr(list_y)

    hist=ROOT.TH2D(name,name,channels,0.9*np.min(array_x),1.1*np.max(array_x),channels,0.9*np.min(array_y),1.1*np.max(array_y))
    fill_h(hist,array_x, array_y)
    hist.SetLineColor(linecolor)
    hist.SetLineWidth(linewidth)
    hist.GetXaxis().SetTitle(x_name)
    hist.GetYaxis().SetTitle(y_name)
    hist.Write()
    hist.SetStats(False)
    hist.GetYaxis().SetMaxDigits(3);
    hist.GetXaxis().SetMaxDigits(3);
    #hist.Write()
    return hist

def canvas(plot,name="test", size=800, leftmargin=0.1, rightmargin=0.2,tmin=0, tmax=0, Tline=False):
    y_name=plot.GetYaxis().GetTitle()
    x_name=plot.GetXaxis().GetTitle()
    can1=ROOT.TCanvas(name, name)
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
    plot.GetXaxis().SetRangeUser(0.8*tmin, 2*tmax)
    plot.Draw("ALP")

    if Tline==True:
        can1.Update()
        ymax=ROOT.gPad.GetUymax()
        ymin=ROOT.gPad.GetUymin()
        line=ROOT.TLine(tmin,ymin,tmin,ymax)
        line.SetLineColor(2)
        line.SetLineWidth(2)
        line.Draw("SAME")

        line1=ROOT.TLine(tmax,ymin,tmax,ymax)
        line1.SetLineColor(2)
        line1.SetLineWidth(2)
        line1.Draw("SAME")


    can1.Write()
    can1.SaveAs(name+".png")
    return can1

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


main=ROOT.TFile("comparison.root","RECREATE")#root file creation

#test on gain_meas
#cal_off=1.026
#print("Shift is: ", cal_off)

#1)
#fit gain curve
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
#exponential function

#################################
#CALIBRATION OFFSET
#cal_off=1.02
#################################

g=pd.read_csv(  "../26072021/gain-meas.csv"  ,   usecols=["V","G","err"] ,  delimiter=";"  )
gnew=pd.read_csv("gain-meas.csv", usecols=["V","G","err"],  delimiter=";" )


Exponential=ROOT.TF1("Exponential","[0]*exp([1]*x)",min(gnew["V"]),max(gnew["V"]))
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


#GAIN OLD
plot1 = ROOT.TGraphErrors(len(g["V"]),  np.array(g["V"]  ,dtype="d")  ,  np.array(g["G"]  ,dtype="d") , 1E-9*np.array(   g["err"]   ,dtype="d"),np.array(  g["err"]    ,dtype="d"))
plot1.SetTitle("Old Gain vs Voltage")
plot1.SetName("Old Gain vs Voltage")
plot1.GetXaxis().SetTitle("Voltage (V)")
plot1.GetYaxis().SetTitle("Gain")
plot1.SetMarkerColor(3)#blue
plot1.SetMarkerStyle(23)
plot1.SetMarkerSize(2)
#plot1.SetDrawOption("C");#smooth curve
plot1.Fit("Exponential", "RQ","r")
plot1.Write()

#GAIN NEW
a=0.389036309
e_a=9.55E-05
b=0.454501552
e_b=9.99E-05

T0=	296.38
P0=	95912


def correction(G,err_G,t,p,A):
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

gcorr=correction(gnew["G"], gnew["err"], 297.58, 96374, 8.6E-8)

plot = ROOT.TGraphErrors(len(gnew["V"]),  np.array(gnew["V"]  ,dtype="d")  ,   gcorr[0] , 1E-9*np.array(   gnew["err"]   ,dtype="d"),gcorr[1])
plot.SetTitle("New Gain vs Voltage")
plot.SetName("New Gain vs Voltage")
plot.GetXaxis().SetTitle("Voltage (V)")
plot.GetYaxis().SetTitle("Gain")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(2)
#plot.SetDrawOption("C");#smooth curve
plot.Fit("Exponential", "RQ","r")
plot.Write()

mg=ROOT.TMultiGraph()
mg.Add(plot)
mg.Add(plot1)



#ROOT.gStyle.SetOptFit()

mg.Draw("AP")
mg.SetNameTitle("New Gain vs Voltage","New Gain vs Voltage")
mg.GetXaxis().SetTitle("Voltage (V)")
mg.GetYaxis().SetTitle("Gain")


cv.Write()
#cv.SetLogy()
cv.Update()

leg = ROOT.TLegend(0.2,0.7330595,0.6,0.8829569);
#leg.SetHeader("The Legend Title");
leg.AddEntry(plot,"New Gain");
leg.AddEntry(plot1,"Old Gain");
leg.Draw("SAME");


cv.SaveAs("gainVSvoltage_diff.pdf")
cv.SaveAs("gainVSvoltage_diff.png")

########################################################################################################################################################################################################################################################################################################################################################################################################################################################################




########################################################################################################################################################################################################################################################################################################################################################################################################################################################################









#
#
#
#
#
#
