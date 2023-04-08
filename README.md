# 0 Ensure the synchronization of the remote log directory
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
To set the fit you should edit the `anal_parameters.txt` file. An example:
```
points;<numer of point to sample in the a,b plane>
a_min;<min of the a range>
a_max;<max of hte a range>
b_min;<min of the b range>
b_max;<max of the b range>
err_step;<step in the a and b directions for tha algorithm that look for the error>
```
**Pay attention to the number of points, you can go out of memory easily, 1000 is a good number if the range is not so large**
The code asks you to select the name of the dataset generated that you want to fit. Also in this case you can specify with the `-n` argument the name of the output files. The latter is a .root file with the graph, a .csv with the results in tabular form and a .pdf and a .png with the chi2 plot in the a,b plane.
### 3.1.2 MinimizingVariance folder
This code works similarly to the TP_Fit one. It has the same `anal_parameters.txt` file, but ir works differently. It doesn't use the correction model and fit the data but it applies the correction for a set of randomly generated *a* and *b* and it chose the pair that minimizes the variance of the final dataset. For this reason, this procedure is less dependent on the calibration (depends only on *A* and not on *B*) and form experience works slightly better than the fit.