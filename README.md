# lcls-cu-acc-live

This project contains the tools for running the online Bmad model for the copper beamline (at present only cu_hxr) and syncing the online model with process variables collected from the live accelerator. 


## Environment

The environment for this project may be set up using conda using the included `environment.yml`:

```
$ conda env create -f environment.yml
```

Once complete, activate the environment:

```
$ conda activate lcls-cu-inj-live
```

Install the project locally:
```
$ pip install -e .
```

Additionally, this project requires a full local installation of [Bmad](https://www.classe.cornell.edu/bmad/) and a local copy of [lcls-lattice](https://github.com/slaclab/lcls-lattice) files.


## Starting the server

In order for the model to run, the following environment variables must be set:

| Variable     | Description                                   |
|--------------|-----------------------------------------------|
| LCLS_LATTICE | Path to lcls-lattice package on local machine |
| ACC_ROOT_DIR | Path to local Bmad installation               |


### Remote EPICS access

This project defines a bridge for the purpose of syncing live accelerator variables with the model. This bridge will run in a separate shell from the server and make use of `lcls-live` utility functions for configuring remote access to EPICS variables. In order to do this, the following variables must be set:

| Variable            | Description                          |
|---------------------|--------------------------------------|
| CA_NAME_SERVER_PORT | Port for forwarding                  |
| LCLS_PROD_HOST      | Production host of process variables |
| SLAC_MACHINE        | Public SLAC machine for forwarding   |
| SLAC_USERNAME       | Username passed to ssh               |


Once set, remote EPICS access may be configured in the bridge shell using the command:

```
$ configure-epics-remote
```

This will create a background process, which will need to be manually killed via pid number after termination.

```
$ ps aux | grep ssh 
```

### Plots

In a third window, serve the bokeh display using the command:

```
$ bokeh serve lcls_cu_acc_live/plots.py --show
```