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

    hist=ROOT.TH1D(x_name,x_name,channels,0.9*np.min(array),1.1*np.max(array))
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




print("#################################################################################################################")
print("         Chose the REFERENCE dataset: ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../TP_correction/*.csv")
print("#################################################################################################################")
reference=input("Insert only the datset name: ")
#to_corr="Dataset_2021-09-22_2021-10-20"

print("#################################################################################################################")
print("         Chose the dataset to analyze (write 'same' to sun the anaysis on the same dataset): ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../TP_correction/*.csv")
print("#################################################################################################################")
in_string=input("Insert only the datset name: ")
if in_string=="same":
    to_anal=reference
else:
    to_anal=in_string


df_ref=pd.read_csv("../TP_correction/"+str(reference)+".csv", delimiter=";")
df_anal=pd.read_csv("../TP_correction/"+str(to_anal)+".csv", delimiter=";")

print("#################################################################################################################")
print("CSV file columns: ")
col_ref=df_ref.columns
col_anal=df_anal.columns
print(col_ref)
print("#################################################################################################################")
"""
df_anal=pd.read_csv("../TP_correction/"+str(reference)+".csv", delimiter=";")

print("#################################################################################################################")
print("CSV file columns: ")
col_anal=df_ref.columns
print(col_anal)
print("#################################################################################################################")
"""

if in_string=="same":
    main=ROOT.TFile("Root_"+str(reference)+"_analyzed_with_same.root","RECREATE")
else:
    main=ROOT.TFile("Root_"+str(reference)+"_analyzed_with_"+str(to_anal)+".root","RECREATE")


#plot the histogram and scatter of reference and anal dataset
main.mkdir("plots")
main.cd("plots")

time_ref=np.arange(0,len(df_ref[col_ref[0]]))
etime_ref=1E-20*np.ones(len(df_ref[col_ref[0]]))

time_anal=np.arange(0,len(df_anal[col_anal[0]]))
etime_anal=1E-20*np.ones(len(df_anal[col_anal[0]]))


plot_ref=grapherr(time_ref, df_ref[col_ref[0]], etime_ref, df_ref[col_ref[1]], "Time (a.u.)", "Corrected gain Reference" , 4, 22)
hist_ref=hist(df_ref[col_ref[0]], "Corrected gain reference", 1000, 4)

plot_anal=grapherr(time_anal, df_anal[col_anal[0]], etime_anal, df_anal[col_anal[1]], "Time (a.u.)", "Corrected gain Anal" , 4, 22)
hist_anal=hist(df_anal[col_anal[0]], "Corrected gain anal", 1000, 4)



#computing mean and std reference and acquiring

ref_gain=nparr(df_ref[col_ref[0]])
err_ref_gain=nparr(df_ref[col_ref[1]])
anal_gain=nparr(df_anal[col_anal[0]])
err_anal_gain=nparr(df_anal[col_anal[1]])

mean=np.mean(ref_gain)
sigma=np.std(ref_gain)
av=10
print("mu:", mean, "sigma:", sigma)
#function for t-calculation

def tvalue(sample, error):
    tvalues=np.empty(len(sample)-av)
    for i in range(len(tvalues)):
        temp_m=np.mean(sample[i:i+av])
        temp_s=np.std(sample[i:i+av])

        #print(mean, temp_m, sigma, temp_s)
        tvalues[i]=(mean-temp_m)/(m.sqrt(sigma*sigma+temp_s*temp_s))

    return tvalues


t_anal=tvalue(anal_gain, err_anal_gain)

main.cd()

plot=graph(time_anal[:-10], t_anal, "Time (a.u.)", "t_values" , 4, 22)
c_plot=canvas(plot)
c_plot.SaveAs("./output_plots/"+"Ref_"+str(reference)+"_Anal_"+str(in_string)+"tVStime.png")
c_plot.SaveAs("./output_plots/"+"Ref_"+str(reference)+"_Anal_"+str(in_string)+"tVStime.pdf")


hist=hist(t_anal, "t_values", channels=1000)
c_hist=ROOT.TCanvas("t_values","t-values", 800, 800)
c_hist.SetFillColor(0);
c_hist.SetBorderMode(0);
c_hist.SetBorderSize(2);
c_hist.SetTopMargin(0.1);
c_hist.SetBottomMargin(0.1);
c_hist.SetFrameBorderMode(0);
c_hist.SetFrameBorderMode(0);
c_hist.SetFixedAspectRatio();
hist.Draw()
c_hist.Write()
c_hist.SaveAs("./output_plots/"+"Ref_"+str(reference)+"_Anal_"+str(in_string)+"tdistr.png")
c_hist.SaveAs("./output_plots/"+"Ref_"+str(reference)+"_Anal_"+str(in_string)+"tdistr.pdf")

#create DataFrame
dt=pd.DataFrame( { "tvalues":t_anal  } )
#write dataframe
if in_string=="same":
    dt.to_csv("Analyzed_"+str(to_anal)+"_with_same.csv", sep=';', header=True, index=False, mode='w')
else:
    dt.to_csv("Analyzed_"+str(to_anal)+"_with_"+str(reference)+".csv", sep=';', header=True, index=False, mode='w')





































#
#
#
#
#
#
