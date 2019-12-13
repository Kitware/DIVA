# ** NOTE ** Currently this Dockerfile depends on a non-public Kwiver
# Docker image (due to pending changes in Kwiver)
FROM kitware/kwiver:_latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    build-essential \
                    libgl1-mesa-dev \
                    libexpat1-dev \
                    libgtk2.0-dev \ 
                    liblapack-dev \
                    git \
                    vim \
                    wget \
                    cmake-curses-gui \
                    libssl-dev \
                    python3-dev \
                    python3-pip \
                    && pip3 install numpy scipy setuptools six

# Ensure python3 is the default
WORKDIR /usr/bin
RUN ln -sf python3 python

ENV DIVA_BASE=/diva
ENV DIVA_INSTALL=/opt/diva
ENV KWIVER_INSTALL=/usr/local/lib/kwiver
ENV DIVA_SRC=${DIVA_BASE}/src
ENV DIVA_BUILD=${DIVA_BASE}/build
ENV DIVA_TEMP=${DIVA_BASE}/tmp

WORKDIR ${DIVA_BASE}

# build DIVA framework
RUN ln -sf /usr/local/cuda/lib64/stubs/libcuda.so /usr/local/cuda/lib64/libcuda.so
RUN mkdir -p ${DIVA_SRC}
ADD CMake ${DIVA_SRC}/CMake
ADD algo ${DIVA_SRC}/algo
ADD drivers ${DIVA_SRC}/drivers
ADD external ${DIVA_SRC}/external
ADD etc ${DIVA_SRC}/etc
ADD processes ${DIVA_SRC}/processes
ADD utils ${DIVA_SRC}/utils
ADD scripts ${DIVA_SRC}/scripts
ADD CMakeLists.txt ${DIVA_SRC}/CMakeLists.txt
ADD python ${DIVA_SRC}/python

RUN mkdir -p ${DIVA_BUILD}
WORKDIR ${DIVA_BUILD}

RUN cmake ${DIVA_SRC} \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${DIVA_INSTALL} \
    -DKWIVER_PYTHON_MAJOR_VERSION=3 \
    -DDIVA_PYTHON_MAJOR_VERSION=3 \
    -DDIVA_BUILD_WITH_CUDA=ON \
    -DDIVA_BUILD_WITH_CUDNN=ON \
    -DDIVA_ENABLE_PROCESS=ON \
    -DDIVA_SUPERBUILD=OFF
RUN make -j8
RUN make install
WORKDIR /

# Setup_kwiver env variables
ENV VG_PLUGIN_PATH=${DIVA_INSTALL}
ENV PATH=${DIVA_INSTALL}/bin:${PATH}
ENV LD_LIBRARY_PATH=${DIVA_INSTALL}/lib:/usr/local/lib:${LD_LIBRARY_PATH}
ENV KWIVER_PLUGIN_PATH=${KWIVER_INSTALL}/modules:${KWIVER_INSTALL}/processes:${KWIVER_PLUGIN_PATH}
# Append here
ENV VITAL_LOGGER_FACTORY=${KWIVER_INSTALL}/modules/vital_log4cplus_logger
ENV LOG4CPLUS_CONFIGURATION=/usr/local/log4cplus.properties
# Python environment
ENV PYTHON_LIBRARY="/usr/lib/x86_64-linux-gnu/libpython3.5m.so"
ENV PYTHONPATH=${DIVA_INSTALL}/lib/python3/dist-packages:${PYTHONPATH}
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages/kwiver:${PYTHONPATH}
ENV PYTHONPATH=/usr/local/lib/python3/dist-packages:${PYTHONPATH}
ENV SPROKIT_PYTHON_MODULES=kwiver.processes

# Setup_diva env variables
ENV KWIVER_PLUGIN_PATH=${DIVA_INSTALL}/lib/diva/processes:${DIVA_INSTALL}/lib/diva/modules:${KWIVER_PLUGIN_PATH}
ENV SPROKIT_PYTHON_MODULES=DIVA.processes:DIVA.processes.rc3d:DIVA.processs.act:${SPROKIT_PYTHON_MODULES}
