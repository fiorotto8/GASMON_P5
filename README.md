# Ensure the syncronization of the remote log directory
Raw data are store in ~/GasMon/Readout/logs/ on the remote machine. We use ```rsync``` to sincronize the local folder All_data/logs.
The GasMon PC is not open to direct connection outside CERN so a tunnel to a lxplus machine (or any PC on the CERN General Network is required)
### Add on your machine's ~/.ssh/config
```
Host lxplus
    HostName lxplus.cern.ch
    User <your CERN username>
Host gasmon_outside
    HostName 128.141.91.109
    User gem3
    ProxyJump lxplus
```
### Run All_data/download_data.sh
Passwords of your lxplus and later of the GasMon machine are requested


0)  In 'Gain_FIT' the gain vs voltage charateristic at P0 and T0 is fitted to obtain A and B the input file is 'gain_meas.csv'
    the output file 'anal_parameters.csv' is written here with such parameters and the errors

1)  In 'All_data' are present all the files download by the GASMON PC.
    To update its content log on your lxplus and run the script All_data/download_data.sh (you should kwon the GASMON PC password)

2)  In 'Script_downloadAggregate' you can create a large csv file with all the parameters.
    You need to specify the time range (pay attention to the date format)
    It will output a file: 'Dataset_start-end.csv' with additionally the rate and gain measured (+ errors).

3) In 'TP_Fit' folder you can fit a seected range of data with the TP correction funciton
   The anal_parameters.csv contains the P0, T0 and V from the QC5 and the parametrs regarding the fit (range of a and b and step)
   It will output a file: results_dataset_...csv with the fit parameters and their errors

4) In 'TP_correction' folder you can correct a set of data with a selected fit parameters from a certin data fit
   It will output a file with the corrected dataset and a root file witht he comparison between correted and uncorrected one

5) In 'tvalues' folder the t-values are computed starting from a certain dataset corrected in a certin way (taken from TP_correction)
   You have to chose the datset where to compute the t values and the dataset to use as reference

6) In 'FakeWarning_Probability' you can simulate the false positive probability
   pointBYpoint_calcualtor.py generates a sample of data points that drift away from the average little by little tvalues are also calculated to see where the warning is generated
   dataset_calcualtor.py (points) is used to create a datsample both extracting directly from the distribution and just a gaussian extraction
   N.B --> Since this is not enough, qualntiles.py computes the areaas of the distribution of the t-balues from a given dataset
   plot.py plots the probabilities from the quantilies entimation and the extraction both from pavia and P5

7) In 'Performance_Simulation' you can simulate the response of the algorithm
   simulation_xtraction.py extarct random the gain values from the distribution and drift it from the nominal, this works fine because is not representative of real sitautions
   simulation_withDataset.py use a piece of a real dataaset and drift a part of it, this is representative of a typical sitution

