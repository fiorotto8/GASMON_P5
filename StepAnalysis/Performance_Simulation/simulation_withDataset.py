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
import argparse

ROOT.gROOT.SetBatch(True)

parser = argparse.ArgumentParser()
parser.add_argument("-b", "--bin", help="Set the number of bins of the histograms",default="1000")
args = parser.parse_args()

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


bins=int(args.bin)

main=ROOT.TFile("Simualted_"+str(reference)+"_fakeWarningDataset.root","RECREATE")
#plot the histogram and scatter of reference and anal dataset
main.mkdir("plots")
main.cd("plots")

time_ref=np.arange(0,len(df_ref[col_ref[0]]))
etime_ref=1E-20*np.ones(len(df_ref[col_ref[0]]))
ref_gain=nparr(df_ref[col_ref[0]])
err_ref_gain=nparr(df_ref[col_ref[1]])

plot_ref=grapherr(time_ref, df_ref[col_ref[0]], etime_ref, df_ref[col_ref[1]], "Time (a.u.)", "Corrected gain Reference" , 4, 22)
hist_ref=hist(df_ref[col_ref[0]], "Corrected gain reference", bins, 4)


main.mkdir("simulation")
main.cd("simulation")
sel_data=ref_gain[-20000:]
sel_time=np.arange(0,len(sel_data))
plot = graph(sel_time, sel_data, "Time (a.u.)", "Selected dataset" , 4, 22)

sim_data=np.empty(len(sel_data))
step=0.5
offset=10000
for i in range(len(sel_data)):
    if i<offset:
        sim_data[i]=sel_data[i]
    else:
        sim_data[i]=sel_data[i]+(step*(i-offset))

plot_gain = graph(sel_time, sim_data , "Time (a.u.)", "Simulated dataset" , 4, 22)


mean=np.mean(ref_gain)
sigma=np.std(ref_gain)
av=10
def tvalue(sample):
    tvalues, medie, sigme=np.empty(len(sample)-av),np.empty(len(sample)-av),np.empty(len(sample)-av)
    for i in range(len(tvalues)):
        temp_m=np.mean(sample[i:i+av])
        temp_s=np.std(sample[i:i+av])

        medie[i]=temp_m
        sigme[i]=temp_s
        tvalues[i]=(temp_m-mean)/(m.sqrt(sigma*sigma+temp_s*temp_s))

    #print(len(sample), len(tvalues))
    return [medie, sigme, tvalues]


t_sim=tvalue(sim_data)

plot_t=graph(sel_time[:-10], t_sim[2], "Time (a.u.)", "t_values" , 4, 22)

#look for values that make trigger the alarm

t_star=np.arange(0.1,10,0.1)
g_warning, err_warning=np.empty(len(t_star)),np.empty(len(t_star))
for i in range(len(t_star)):
    for j in range(len(t_sim[2])):
        if t_sim[2][j]>=t_star[i]:
            g_warning[i]=t_sim[0][j]
            err_warning[i]=t_sim[1][j]/m.sqrt(av)
            break;
        else:
            a=0

plot_res=grapherr(t_star,g_warning, 1E-20*t_star , err_warning, "t*", "gain @ warning" , 4, 22)

res=100*((g_warning-mean)/mean)
e_res=100*np.sqrt(   np.square((sigma/len(ref_gain))/mean) + np.square( err_warning/g_warning )  )

plot_res=grapherr(t_star,res, 1E-20*t_star , e_res, "t*", "Gain resolution @ warning (%)" , 4, 22)

cv= ROOT.TCanvas("cv", " ",0,0, 1200,1200)
cv.SetFillColor(0);
cv.SetBorderMode(0);
cv.SetBorderSize(2);
cv.SetLeftMargin(0.12);
cv.SetRightMargin(0.1);
cv.SetTopMargin(0.1);
cv.SetBottomMargin(0.1);
cv.SetFrameBorderMode(0);
cv.SetFrameBorderMode(0);
cv.SetFixedAspectRatio();

plot_res.SetMarkerStyle(4);
plot_res.SetMarkerColor(4);
plot_res.SetLineWidth(2);
plot_res.SetMarkerSize(1.5);
plot_res.SetLineColor(4);
plot_res.Draw("AP");


#cv.SetLogy()
cv.Update()

"""
pt0  = ROOT.TPaveText(-0.0001863652,7.428301,0.4981749,8.247413,"br");
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


pt1  = ROOT.TPaveText(-0.003720842,5.936785,0.4946404,7.538331,"br");
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


ax=plot_res.GetHistogram().GetYaxis()
#ax2=plot_res.GetHistogram().GetYaxis().GetYmax()
min=ax.GetXmin()
max=ax.GetXmax()

#print(log(x/6.66E6)/(-0.194))

#ymin=m.log(min/6.66E6)/(-0.194)
#print(max)
ymax=0.164*max-0.152
ymin=0.164*(min)-0.02
#ymin=m.log(min/6.66E6)/(-0.194)
#print(ymax)



func= ROOT.TF1("func","0.164*x-0.152",ymin, ymax);
#func= ROOT.TF1("func","-24.3*x*x*x+2655*x*x-97485*x+1e6",min, max)
#func= ROOT.TF1("func","(2500/69)-(sqrt(46*x-3E5))/138",min, max)

#xaxis
ax=plot_res.GetHistogram().GetXaxis()
ax_min=ax.GetXmin()
ax_max=ax.GetXmax()
#yaxis
ay=plot_res.GetHistogram().GetYaxis()
ay_min=ay.GetXmin()
ay_max=ay.GetXmax()


#y2axis = ROOT.TGaxis(2.103531,0.1039692,2.103531,7.735172,"func" ,50510,"+L");
y2axis = ROOT.TGaxis(ax_max,ay_min,ax_max,ay_max,"func" ,50510,"+L");
y2axis.SetTitle("CO_{2} Concentration Resolution (%)")
y2axis.SetLabelSize(0.03)

y2axis.SetTitleColor(2)
y2axis.SetLineColor(2)
y2axis.SetLabelColor(2);
y2axis.SetTitleSize(0.04)
y2axis.SetTitleOffset(1.2)
y2axis.SetTextFont(42);
y2axis.Draw();

cv.Update()







main.cd()
cv.Write()
#save as pdf and/or png
cv.SaveAs("output_files/"+str(reference)+"_Resolution.root.png");
cv.SaveAs("output_files/"+str(reference)+"_Resolution.root.pdf");
#ROOT.gApplication.Run()


























#
#
#
#
#
#
