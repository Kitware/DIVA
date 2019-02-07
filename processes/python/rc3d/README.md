
# RC3D Pipeline

Steps to execute RC3D using sprokit in an online fashion

# Contents
1. [Pre-Requisites](#pre-requisites)
2. [Preparation](#preparation)
3. [Execution](#execution)

# Pre-Requisites
1. [RC3D](https://gitlab.kitware.com/kwiver/R-C3D) 
2. [DIVA](https://github.com/Kitware/DIVA)

#### Note:  We would refer to the root directory of RC3D repository as `RC3D_ROOT` and root directory of DIVA as 'DIVA_ROOT'

# Preparation
1. Build DIVA using the instructions available [here](https://github.com/Kitware/DIVA).
2. Add experiment folder of virat to your PYTHONPATH using the following
   ```shell
    export PYTHONPATH=RC3D_ROOT/experiments/virat:$PYTHONPATH
   ```

# Execution    
    cd DIVA_ROOT
    pipeline_runner -p pipelines/rc3d/rc3d.pipe
    
    



 
