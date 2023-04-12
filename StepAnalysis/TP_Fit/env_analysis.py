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

ROOT.gROOT.SetBatch(True)


if not os.path.exists("output_plots"):
    os.makedirs("output_plots")

def plot_plot(marker,color,x,y,e_x,e_y,title_x, title_y):

    x=nparr(x)
    e_x=nparr(e_x)
    y=nparr(y)
    e_y=nparr(e_y)

    plot = ROOT.TGraphErrors(len(x),x,y,e_x,e_y  )
    plot.SetNameTitle(title_y+" vs "+title_x,title_y+" vs "+title_x)
    plot.GetXaxis().SetTitle(title_x)
    plot.GetYaxis().SetTitle(title_y)
    plot.SetMarkerColor(color)#blue
    plot.SetMarkerStyle(marker)
    plot.SetMarkerSize(1.5)
    plot.Write()

    return plot


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

f = open("anal_parameters.txt", "r")
print("############################################################")
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
print("         Chose the dataset to analyze ")
print("Copy/Paste one name from the following list, if it is not present you should generate the dataset")
print("#################################################################################################################")
os.system("ls -lrt ../../Script_downloadAggregate/*.csv")
print("#################################################################################################################")
input=input("Insert only the datset name: ")

df=pd.read_csv("../../Script_downloadAggregate/"+str(input)+".csv", delimiter=";")

#compute from scratch rate, gain and error
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

rate=rate_calc(df["Timestamp"],r0,folder)
print(rate)
gain=-1*nparr(df["Mean Current"])/(200*1.6E-19*rate)
err_gain=nparr(df["Mean Error"])/(200*1.6E-19*rate)



print("#################################################################################################################")
print("CSV file columns: ")
col=df.columns
print(col)
print("#################################################################################################################")


#get average of T, P and gain form the first 1000 samples of hte dataset
main=ROOT.TFile("root_"+str(input)+".root","RECREATE")

time_all=np.arange(0,len(df[col[0]]))
etime_all=1E-20*np.ones(len(df[col[0]]))

V=np.mean(nparr(df["Vmon"]))
print("V=",V)

print("Fitting...")
############################################################################################
main.mkdir("Entry Variables")
main.cd("Entry Variables")
#varieables with errorrs
for i in (3,22):
    grapherr(time_all, df[col[i]], etime_all, df[col[i+1]], "Time (a.u.)", col[i] )
#variables without errors
for i in (5,6,7,3,10,13,14,15,19,20,21,24):
    graph(time_all, df[col[i]], "Time (a.u.)", col[i] )
#bonus
graph(time_all, df["T"]/df["P"], "Time (a.u.)", "T/P" )
############################################################################################

############################################################################################
main.mkdir("Meas Gain vs other variables")
main.cd("Meas Gain vs other variables")

for i in (5,6,7,3,10,13,14,15):
    grapherr(df[col[i]], gain, etime_all, err_gain,   col[i], "Gain Measured" )
#bonus
grapherr(df["T"]/df["P"],gain, etime_all, err_gain, "T/P", "Gain Measured" )
############################################################################################

############################################################################################
#graph of the gain vs T and P
main.cd()
gtp=ROOT.TGraph2D(len(df["T"]), nparr(df["T"]),nparr(df["P"]), gain);
gtp.GetXaxis().SetTitle("Temperature")
gtp.GetYaxis().SetTitle("Pressure")
gtp.GetXaxis().SetTitle("Gain Measured")
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

chi=chi2func(gain,err_gain,a,b,nparr(df["P"]),nparr(df["T"]))
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
chi_err=chi2func(gain,err_gain,a_err,b_err,nparr(df["P"]),nparr(df["T"]))
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

pt1  = ROOT.TPaveText(0.55,0.75,0.65,0.85,"NDC");
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
f.write("ndf;"+str(len(df["Gain Measured"])-2)+"\n")
f.write("reduced_chi;"+str(chi[index])+"\n")
f.write("a;"+str(a[index][0])+"\n")
f.write("e_a;"+str(err_a[0])+"\n")
f.write("b;"+str(b[index][0])+"\n")
f.write("e_b;"+str(err_b[0])+"\n")

f.close()

############################################################################################



#####################################################################################################################################################################################################################

def correction_ab_full(G,err_G,a,b,p,t):
    """
    applies the correction for a certain value of a and b
    """

    X=G**(  (P0/p)**(-a)  *  (t/T0)**(-b)   )
    #Y= A**   (  (P0/p)**(a)  *  (t/T0)**(b)    )
    Y= A**   (  (P0/p)**(-a)  *  (t/T0)**(-b)        -1)
    #Y=1
    corr=X/Y

    X=(P0/p)**(-a)
    Y=(t/T0)**(-b)

    err_a=0
    err_b=0

    error=   (A**(1-X*Y)) * (G**(X*Y)) * X * Y * np.sqrt( np.square(err_G/G) +      np.square( err_a*np.log(P0/p)*(np.log(A)-np.log(G)) ) + np.square( (np.log(A)-np.log(G))*err_b*np.log(t/T0) )     )


    return np.array([corr, error], dtype="d")
    #return np.array(corr, dtype="d")



[corr_gain, e_corr_gain]=correction_ab_full(gain, err_gain, a[index], b[index],nparr(df["P"]),nparr(df["T"]))


time=[x for x in range(len(gain))]
err_time=[0.001 for x in range(len(gain))]



####################################################################################################################################
cv=ROOT.TCanvas("Gain","Gain", 800, 800)
cv.SetFillColor(0);
cv.SetBorderMode(0);
cv.SetBorderSize(2);
cv.SetLeftMargin(0.1497996);
cv.SetRightMargin(0.1497996);
cv.SetTopMargin(0.08110883);
cv.SetBottomMargin(0.1190965);
cv.SetFrameBorderMode(0);
cv.SetFrameBorderMode(0);
cv.SetFixedAspectRatio();


plot1=plot_plot(22,4,time,gain,err_time,err_gain,"Time(a.u.)", "Measured Gain")
plot2=plot_plot(23,2,time,corr_gain,err_time,e_corr_gain,"Time(a.u.)", "Corrected Gain")

mg=ROOT.TMultiGraph()

mg.Add(plot1)
mg.Add(plot2)

mg.SetName("Gain vs Time");
mg.GetXaxis().SetTitle("Time(a.u.)")
mg.GetYaxis().SetTitle("Effective gas gain")
mg.GetXaxis().SetTitleSize(0.045);
mg.GetYaxis().SetTitleSize(0.045);
#mg.GetYaxis().SetRangeUser(0,2);
#mg.GetXaxis().SetRangeUser(0,280);
mg.GetYaxis().SetRangeUser(14E3,30E3);
#mg.GetYaxis().SetRangeUser(0,2);
mg.GetYaxis().SetMaxDigits(3);
mg.GetXaxis().SetDecimals();
mg.Draw("AP")

leg = ROOT.TLegend(0.2,0.8,0.4,0.9);
#leg.SetHeader("The Legend Title");
leg.AddEntry(plot1,"Measured Gain");
leg.AddEntry(plot2,"Corrected Gain");

leg.Draw("SAME");

cv.Update()

#save as pdf and/or png
cv.SaveAs("output_plots/GainTime"+str(input)+".png");
cv.SaveAs("output_plots/GainTime"+str(input)+".pdf");
#ROOT.gApplication.Run()

################################################################################################
hist_nocorr=hist(gain, "Gain before correction", 1000, 4)
hist_corr=hist(corr_gain, "Gain after correction", 1000, 2)


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

cv_histo.SaveAs("./output_plots/"+"Corrected_"+str(input)+"_withitself.png");
cv_histo.SaveAs("./output_plots/"+"Corrected_"+str(input)+"_withitself.pdf");

###########################################################################























#
#
#
#
#
#
