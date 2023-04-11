**More info about the full repository and the purpose may be found here:**
[3<sup>rd</sup> chapter of Davide's PhD Thesis](https://cds.cern.ch/record/2803932?ln=en)
# -1 General notes
### The early version of such code has been written during my first tries with Python and it received multiple patches. It's ugly but it works! Any suggestions or modifications are more than welcome!!!

### The `LOG_p5.txt` file contains the date of the important things that happened on the gas system regarding the GASMON system.

### In general, the `.txt` files are synchronized and are required for the good behavior of the infrastructure, while the `.csv`files are related to the dataset so, in general, are not synchronized.
# 0 Setting up the environment

## Install requirements
Just run this command on your machine. You may omit the --user option, but it is mandatory if you work on lxplus.
```
pip3 install --user -r requirements.txt
```
**You also need ROOT to make it work!**

## Ensure the synchronization of the remote log directory
Raw data are stored in ~/GasMon/Readout/logs/ on the remote machine. We use `rsync` to synchronize the local folder All_data/logs.
The GasMon PC is not open to a direct connection outside CERN so a tunnel to a plus machine (or any PC on the CERN General Network is required)
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
Before running, you should give it permissions
```
sudo chmod 777 All_data/download_data.sh
```
Passwords of your plus and later of the GasMon machine are requested.


# 1 Create Dataset
For any kind of the following analysis, you should generate a dataset that spans over a certain amount of time. The raw files from the GasMon are divided into days but the ```Script_downloadAggregate/create_dataset.py``` do the aggregation for you.
When running, the script will ask you for the start date and the stop date. you can write `max` on the start to use the oldest file and `max` on the stop date to use the today value.
The default dataset name is composed of the dates, using `-n` as an argument you can set a dedicated name for the dataset.
**Remember that all the data contained in the generated dataset are the ones from the GasMon machine. The correction and the manipulation made locally by the GasMon system may be different from what you want**
**For monitoring purposes of the _beahvious of GASMON system the_ output `.root` is very useful*
**
# 2 Calibration Data
For most of the analysis you have to do here you need calibration data. In particular, the measurement of the initial gain, rate and temperature and pressure. Such measurements are usually contained in a specific directory with the date. The calibration is required to have a good correction parameter estimation. In particular to have a good measurement of the parameters *A* and *B*.
Every folder contains a `qc5.py` script that takes in input the `.csv` file with the data measured that particular calibration day. the script output the `fit_parameters.txt` file that is used by other codes
For new measurements please copy always the latest folder and keep the same format for the date.

# 3 Step by Step Analysis
We now see how to operate a data analysis locally to check the data and/or to set better values and thresholds. We will use just the measured data and not the processed data. Every directory, from now on, is contained in `StepAnalysis`.
## 3.1 Gain fit
There are two ways to find the best parameters (namely *a* and *b*) for the correction. One fits the data with the model (in `TP_Fit`) and the other uses the model to find which parameters reduce the data variance (in `MinimizingVariance`).
### 3.1.1 TP_Fit directory
To set the fit you should edit the `anal_parameters.txt` file. An example:
```
points;<numer of point to sample in the a,b plane>
a_min;<min of the a range>
a_max;<max of hte a range>
b_min;<min of the b range>
b_max;<max of the b range>
err_step;<step in the a and b directions for tha algorithm that look for the error>
```
**Pay attention to the number of points, you can go out of memory easily, 1000 is a good number, if the range is not so large**
The code asks you to select the name of the dataset generated that you want to fit. Also in this case you can specify with the `-n` argument the name of the output files. The latter is a .root file with the graph, a .csv with the results in tabular form and a .pdf and a .png with the chi2 plot in the a,b plane.
**The correction plot you can find in the `.root` file is just to have a visual check about the correction made by the selected parameter, real correction for the next analysis step has to be done inside the `TP_correction` folder**
### 3.1.2 MinimizingVariance folder
This code works similarly to the TP_Fit one. It has the same `anal_parameters.txt` file, but it works differently. It doesn't use the correction model and fit the data but it applies the correction for a set of randomly generated *a* and *b* and it chose the pair that minimizes the variance of the final dataset. For this reason, this procedure is less dependent on the calibration (depends only on *A* and not on *B*) and form experience works slightly better than the fit.
**The correction plot you can find in the `.root` file is just to have a visual check about the correction made by the selected parameter, real correction for the next analysis step has to be done inside the `TP_correction` folder**

## 3.2 TP_correction folder
The correction is already made by the parameter finding codes TP_Fit and MinimingVariance. Here we generate the corrected dataset to be used in further analysis. Also in this case you can give a name to the dataset. Moreover, you can skip the method selected during code running by passing 'm' of 'f' as an argument using `-m`
For this piece of code you cannot set a name because the name of the output file will keep track of the corrected dataset and the dataset used to correct

## 3.3 Performance_Simualtion folder
Here one dataset from the TP_correctin folder is used to measure the performance of the deviation algorithm. To test the performance you need a 'good' dataset. What the code does is artificially increase the points of the dataset by summing a straight line to the real points. It outputs some check plots in the `.root` file, the main output is the Algorithm resolution as a function of the threshold imposed.

## 3.4 tvalues folder
In this folder, you can generate the t_values trend and distribution by selecting a reference dataset and a dataset to test on it

## 3.5 FakeWarning_Probability

Starting for a corrected dataset, usually in this case you usually use a good reference one. The script executes a scan of threshold values and check the probability of having a warning on a given dataset

# 4 Percentage Scan
Usually before the end-of-year technical stop, we perform a scan of the CO2 percentage from the mixer to check if the calibration to pass from gain to CO2 is still the same. Usually, the scans are made from 35% to 25% of CO2 in a step of 5%. Copying the existing folder (2022 is there) and renaming it for the next calibration is enough. You should generate the dataset from the ususal `Script_downloadAggregate/create_dataset.py` script just in the interesting period. During the test pay attention to taking note of the change in percentage and write them down in the `timing_percentage.txt` in the same format as the old files. The code `percentage_analysis` requires some inputs to work such as the gain calibration, the dataset to use (the one you generated) and the T, P correction you want to use.
