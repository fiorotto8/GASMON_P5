# 0 Ensure the synchronization of the remote log directory
Raw data are stored in ~/GasMon/Readout/logs/ on the remote machine. We use `rsync` to synchronize the local folder All_data/logs.
The GasMon PC is not open to a direct connection outside CERN so a tunnel to a lxplus machine (or any PC on the CERN General Network is required)
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
To run it you should give it permissions
```
sudo chmod 777 All_data/download_data.sh
```
Passwords of your plus and later of the GasMon machine are requested.

# 1 Create Dataset
For any kind of the following analysis, you should generate a dataset that spans over a certain amount of time. The raw files from the GasMon are divided into days but the ```Script_downloadAggregate/create_dataset.py``` do the aggregation for you.
When running, the script will ask you for the start date and the stop date. you can write `max` on the start to use the oldest file and `max` on the stop date to use the today value.
The default dataset name is composed of the dates, using `-n` as an argument you can set a dedicated name for the dataset.
**Remember that all the data contained in the generated dataset are the ones from the GasMon machine. The correction and the manipulation made locally by the GasMon system may be different from what you want**

# 2 Calibration Data
For most of the analysis you have to do here you need calibration data. In particular, the measurement of the initial gain, rate and temperature and pressure. Such measurements are usually contained in a specific directory with the date. The calibration is required to have a good correction parameter estimation. In particular to have a good measurement of the parameters *A* and *B*.
Every folder contains a `qc5.py` script that takes in input the `.csv` file with the data measured that particular calibration day. the script output the `fit_parameters.txt` file that is used by other codes
For new measurements please copy always the latest folder and keep the same format for the date.

# 3 Step by Step Analysis
We now see how to operate a data analysis locally to check the data and/or to set better values and thresholds. We will use just the measured data and not the processed data. Every directory, from now on, is contained in `GASMON_WorkingDirectory_stepBYstep`.
## 3.1 Gain fit
There are two ways to find the best parameters (namely *a* and *b*) for the correction. One fits the data with the model (in `TP_Fit`) and the other uses the model to find which parameters reduce the data variance (in `MinimizingVariance`).
### 3.1.1 TP_Fit directory
To set the fit you should edit the `anal_parameters.csv` file. An example:
```
points;<numer of point to sample in the a,b plane>
a_min;<min of the a range>
a_max;<max of hte a range>
b_min;<min of the b range>
b_max;<max of the b range>
err_step;<step in the a and b directions for tha algorithm that look for the error>
```
**Pay attention to the number of points you can go out of memory easily, 1000 is a good number if the range is not so large**
The code asks you to select the name of the dataset generated that you want to fit. Also in this case you can specify with the `-n` argument the name of the oputput files. The latter is a .root file with the graph, a .csv with the results in tabular form and a .pdf and a .png with the chi2 plot in the a,b plane.


0)  In 'Gain_FIT' the gain vs voltage characteristic at P0 and T0 is fitted to obtain A and B the input file is 'gain_meas.csv'
    the output file 'anal_parameters.csv' is written here with such parameters and the errors

1)  In 'All_data' are present all the files downloaded by the GASMON PC.
    To update its content log on to your lx plus and run the script All_data/download_data.sh (you should know the GASMON PC password)

2)  In 'Script_downloadAggregate' you can create a large CSV file with all the parameters.
    You need to specify the time range (pay attention to the date format)
    It will output a file: 'Dataset_start-end.csv' with additionally the rate and gain measured (+ errors).In the 'TP_Fit' folder you can fit a seected range of data with the TP correction function The anal_parameters.csv contains the P0, T0 and V from the QC5 and the parameters regarding the fit (range of a and b and step)
   It will output a file: results_dataset_...csv with the fit parameters and their errors

4) In 'TP_correction' folder you can correct a set of data with a selected fit parameters from a certin data fit
   It will output a file with the corrected dataset and a root file witht he comparison between correted and uncorrected oneIn the 'tvalues' folder the t-values are computed starting from a certain dataset corrected in a certain way (taken from TP_correction)
   You have to choose the datset where to compute the t-values and the dataset to use as a reference

6) In 'FakeWarning_Probability' you can simulate the false positive probability
   pointBYpoint_calcualtor.py generates a sample of data points that drift away from the average little by little tvalues are also calculated to see where the warning is generated
   dataset_calcualtor.py (points) is used to create a datsample both extracting directly from the distribution and just a gaussian extraction
   N.B --> Since this is not enough, qualntiles.py computes the areaas of the distribution of the t-balues from a given dataset
   plot.py plots the probabilities from the quantilies entimation and the extraction both from pavia and P5

7) In 'Performance_Simulation' you can simulate the response of the algorithm
   simulation_xtraction.py extarct random the gain values from the distribution and drift it from the nominal, this works fine because is not representative of real situations simulation_withDataset.py use a piece of a real dataaset and drift a part of it, this is representative of a typical sitution

