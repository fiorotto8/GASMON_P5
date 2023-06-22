import pandas as pd
import numpy as np
import ROOT
import statistics as stat
import math as m

def nparr(list):
    return np.array(list, dtype="d")
#define filling histogram function
def fill_h(histo_name, array):
    for x in range (len(array)):
        histo_name.Fill((np.array(array[x] ,dtype="d")))

input_file="22062023.csv"
main=ROOT.TFile("anal-qc5.root","RECREATE")#root file creation

col=["Start","Stop",	"Voltage","Imon",	"Current",	"err C",	"Rate", "ErrRate"]
data =  pd.read_csv(  input_file  ,   usecols=col ,  delimiter=";"  )
errV=[1 for x in range(len(data["Voltage"]))]


n0=200

enviroment=pd.read_csv("env.csv",sep=";",header=None,names=["Temperature(K)","Pressure(Pa)","Humidity(%)"])
#print(enviroment)

T0=np.mean(nparr(enviroment["Temperature(K)"]))
P0=np.mean(nparr(enviroment["Pressure(Pa)"]))
H0=np.mean(nparr(enviroment["Humidity(%)"]))
e=1.6E-19
time=60#seconds

rate=nparr(data["Rate"])
err_rate=nparr(data["ErrRate"])



#fit current curve
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
#exponential function
Exponential=ROOT.TF1("Exponential","[0]*exp([1]*x)",min(data["Voltage"]),max(data["Voltage"]))
Exponential.SetParNames("Constant","Slope")
Exponential.SetParameters(1E-21,8E-3)



plot = ROOT.TGraphErrors(len(data["Voltage"]),  np.array(data["Voltage"] ,dtype="d")  , np.array(data["Current"] ,dtype="d")  ,np.array(errV ,dtype="d"), np.array(data["err C"] ,dtype="d")    )
plot.SetTitle("Anodic current vs Voltage")
plot.SetName("Anodic Current vs Voltage")
plot.GetXaxis().SetTitle("Voltage (V)")
plot.GetYaxis().SetTitle("Anodic Current")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.SetDrawOption("C");#smooth curve
plot.Fit("Exponential", "RQ","r")
plot.Write()
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################



#compute divider resistance and plot
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
Vset=nparr(data["Voltage"])
Imon=nparr(data["Imon"])



plot = ROOT.TGraph(len(Vset), Imon, Vset   )
plot.SetTitle("Vset vs Imon")
plot.SetName("Vset vs Imon")
plot.GetXaxis().SetTitle("Vset (V)")
plot.GetYaxis().SetTitle("Imon (#mu A)")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.SetDrawOption("C");#smooth curv
plot.Fit("pol1", "RQ", "", min(Imon), max(Imon))
plot.Write()

Req=Vset/Imon

av_Req=np.mean(Req)

off=1E-4

hist=ROOT.TH1D("Equivalent resistance"," ",10,(1-off)*min(Req),(1+off)*max(Req))
fill_h(hist,Req)
hist.Write()

########################################################################################################################################################################################################################################################################################################################################################################################################################################################################



#fit gain curve
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
sigmoid=ROOT.TF1("sigmoid", "([0]/(1+ exp(-[1]*(x-[2]))))",min(data["Voltage"]),max(data["Voltage"]))
sigmoid.SetParameters(375, 0.064, 3182)


plot = ROOT.TGraphErrors(len(data["Voltage"]),  np.array(data["Voltage"] ,dtype="d")  ,rate  ,np.array(errV ,dtype="d"), err_rate    )
plot.SetTitle("Rate vs Voltage")
plot.SetName("Rate vs Voltage")
plot.GetXaxis().SetTitle("Voltage (V)")
plot.GetYaxis().SetTitle("Hit rate (Hz)")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.SetDrawOption("C");#smooth curve
plot.Fit("sigmoid", "RQ","r")
plot.Write()
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################

#hit rate @ max efficiency
rate_plateau=sigmoid.GetParameter(0)
e_rate_plateau=sigmoid.GetParError(0)
#print(rate)

#gain calcualtion
gain=-1*np.array(data["Current"] ,dtype="d")/(rate_plateau*e*n0)
e_gain=gain*np.sqrt( np.square(np.array(data["err C"] ,dtype="d")/np.array(data["Current"] ,dtype="d"))   +       np.square(e_rate_plateau/rate_plateau))



#fit gain curve
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################
Exponential.SetParameters(7E-8,8E-3)

plot = ROOT.TGraphErrors(len(data["Voltage"]),  np.array(data["Voltage"] ,dtype="d")  ,gain  ,np.array(errV ,dtype="d"), e_gain    )
plot.SetTitle("Effective Gas gain vs Voltage")
plot.SetName("Effective Gas gain vs Voltage")
plot.GetXaxis().SetTitle("Voltage (V)")
plot.GetYaxis().SetTitle("Effective Gas gain")
plot.SetMarkerColor(4)#blue
plot.SetMarkerStyle(22)
plot.SetMarkerSize(1)
plot.SetDrawOption("C");#smooth curve
plot.Fit("Exponential", "RQ","r")
plot.Write()
########################################################################################################################################################################################################################################################################################################################################################################################################################################################################


col_write=["A","eA", "B","eB", "T0", "P0", "H0", "Vset", "r0", "Rdivider"]
write=[Exponential.GetParameter(0),Exponential.GetParError(0),Exponential.GetParameter(1),Exponential.GetParError(1),T0,P0, H0, m.log(19692.9/Exponential.GetParameter(0))/Exponential.GetParameter(1), rate_plateau, av_Req]

for i in range(len(col_write)):
    print(col_write[i], write[i])

#create DataFrame
df=pd.DataFrame( {"Col": col_write, "Parameters": write  } )
#write dataframe
df.to_csv("fit_parameters.txt", sep=';', header=False, index=False, mode='w')




#create DataFrame
gain_meas=pd.DataFrame( {"V": Vset, "G": gain, "err":e_gain, "RatePlat": rate_plateau*np.ones(len(Vset))  } )
#write dataframe
gain_meas.to_csv("gain-meas.csv", sep=';', header=True, index=False, mode='w')































#
#
#
#
#
#
#
#
