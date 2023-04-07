import numpy as np
import ROOT
import pandas as pd
from array import array
import os

plot_name="Fake warning porbability VS threshold"
x_axis_name="Threshold t*"
y_axis_name="Algorithm Fake Warning Probability"



onlyfiles = [f for f in os.listdir("output_temp_files") if os.path.isfile(os.path.join("output_temp_files", f))]
#print(onlyfiles)

thresholds, prob, err=np.empty(len(onlyfiles)),np.empty(len(onlyfiles)),np.empty(len(onlyfiles))

for i,f in enumerate(onlyfiles):
    file = open("output_temp_files/"+f, "r")
    line=file.readline()
    content=line.split(";")
    thresholds[i]=content[0]
    prob[i]=content[1]
    err[i]=content[2]

#import from standard file x,ex,y,ey
columns=["x","ex","y","ey"]
#columns=["x"]
df=pd.read_csv(  "Pavia_data.csv"  ,   delimiter=";"  )

x,y,ex,ey=array( 'd' ), array( 'd' ),array( 'd' ), array( 'd' )

for i in range(len(df["x"]) ):
    x.append( df["x"][i])
    ex.append(df["ex"][i])
    y.append( df["y"][i])
    ey.append( df["ey"][i])


df1=pd.read_csv("ProbfromQuantiles.csv", delimiter=";")

x1,y1,ex1,ey1=array( 'd' ), array( 'd' ),array( 'd' ), array( 'd' )

for i in range(len(df1["x"]) ):
    x1.append( df1["x"][i])
    ex1.append(df1["ex"][i])
    y1.append( df1["y"][i])
    ey1.append( df1["ey"][i])




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



mg=ROOT.TMultiGraph()




#first plot options
#copy and paste to add new ones
plot = ROOT.TGraphErrors(len(onlyfiles),  thresholds,prob, 1E-20*thresholds, err)
plot.SetMarkerStyle(4);
plot.SetMarkerColor(4);
plot.SetLineWidth(2);
plot.SetMarkerSize(1.5);
plot.SetLineColor(4);

#first plot1 options
#copy and paste to add new ones
plot1 = ROOT.TGraphErrors(len(df["x"]),  x,y,ex,ey)
plot1.SetMarkerStyle(4);
plot1.SetMarkerColor(2);
plot1.SetLineWidth(2);
plot1.SetMarkerSize(1.5);
plot1.SetLineColor(2);


#first plot1 options
#copy and paste to add new ones
plot2 = ROOT.TGraphErrors(len(df1["x"]),  x1,y1,ex1,ey1)
plot2.SetMarkerStyle(4);
plot2.SetMarkerColor(6);
plot2.SetLineWidth(2);
plot2.SetMarkerSize(1.5);
plot2.SetLineColor(6);


mg.Add(plot);
mg.Add(plot1);
mg.Add(plot2);
#mg.SetTitle(plot_name)
mg.SetName(plot_name);
mg.GetXaxis().SetTitle(x_axis_name)
mg.GetYaxis().SetTitle(y_axis_name)
mg.GetXaxis().SetTitleSize(0.045);
mg.GetYaxis().SetTitleSize(0.045);
#mg.GetYaxis().SetRangeUser(0,2);
#mg.GetXaxis().SetRangeUser(0,280);
mg.GetYaxis().SetRangeUser(1E-10,2);
#mg.GetXaxis().SetRangeUser(0,1.85);
mg.GetYaxis().SetMaxDigits(3);
mg.GetXaxis().SetDecimals();


mg.Draw("AP");

cv.SetLogy()
cv.Update()

"""
pt0  = ROOT.TPaveText(-0.1124256,2.027862,0.389251,4.05004,"br");
pt0.AddText("CMS R&D");
pt0.SetBorderSize(0);
pt0.SetLineColor(1);
pt0.SetLineStyle(1);
pt0.SetLineWidth(2);
pt0.SetFillColor(0);
pt0.SetFillStyle(1001);
pt0.SetTextSize(0.06);
pt0.SetTextFont(42);
pt0.SetTextAlign(11);
pt0.SetFillStyle(3050);
pt0.Draw("SAME")
"""
"""
pt1  = ROOT.TPaveText(28,52628.26,41,165602.6,"br");
pt1.AddText("10x10 cm^{2} Triple-GEM detector");
pt1.AddText("Gap Configuration: 3/1/2/1 mm");
pt1.AddText("Gas: Ar/CO_{2}");
pt1.AddText("Irradiating Source: ^{55}Fe (5.9 keV X-rays)");
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
"""

"""
pt2  = ROOT.TPaveText(21.0071,1310.478,28.9814,3786.434,"br");
pt2.AddText("f(x)=Ae^{-Bx}");
pt2.AddText("A: "+str(  "{:.2e}".format(Exponential.GetParameter(0))     ));
pt2.AddText("B: "+str(  "{:.2e}".format(Exponential.GetParameter(1))  ));
pt2.AddText("#chi^{2}/ndf: "+str(       "{:.2e}".format(Exponential.GetChisquare()/Exponential.GetNDF())      ));
pt2.SetBorderSize(0);
pt2.SetLineColor(1);
pt2.SetLineStyle(1);
pt2.SetLineWidth(2);
pt2.SetFillColor(0);
pt2.SetFillStyle(1001);
pt2.SetTextSize(0.03);
pt2.SetTextFont(42);
pt2.SetTextAlign(11);
pt2.SetTextColor(2);
pt2.SetFillStyle(3050);
pt2.Draw("SAME")

"""


leg = ROOT.TLegend(0.6,0.75,0.95,0.9);
#leg.SetHeader("The Legend Title");
leg.AddEntry(plot,"P5 Simulated");
leg.AddEntry(plot1,"Pavia Simulated");
leg.AddEntry(plot2,"P5 Operation");

leg.Draw("SAME");


cv.Update()







#save as pdf and/or png
cv.SaveAs("output_plots/"+plot_name.replace(" ","_")+".png");
cv.SaveAs("output_plots/"+plot_name.replace(" ","_")+".pdf");
#ROOT.gApplication.Run()












#
#
#
#
#
#
