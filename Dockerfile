FROM nvidia/cuda:9.0-cudnn7-devel-ubuntu16.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    build-essential \
                    libgl1-mesa-dev \
                    libexpat1-dev \
                    libgtk2.0-dev \ 
                    liblapack-dev \
                    python2.7-dev \
                    git \
                    vim \
                    wget \
                    cmake-curses-gui \
                    python-dev \
                    python-numpy \
                    python-pip \
                    python-setuptools \
                    python-scipy \
                    libssl-dev


ENV DIVA_BASE=/diva
ENV DIVA_INSTALL=/opt/diva
ENV DIVA_SRC=${DIVA_BASE}/src
ENV DIVA_BUILD=${DIVA_BASE}/build
ENV DIVA_TEMP=${DIVA_BASE}/tmp




# install cmake
WORKDIR ${DIVA_TEMP}
RUN wget -O cmake-3.12.3.tar.gz https://cmake.org/files/v3.12/cmake-3.12.3.tar.gz && \
    tar xvzf cmake-3.12.3.tar.gz && cd cmake-3.12.3 && \
    ./bootstrap && make -j8 && make install

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
ADD CMakeLists.txt ${DIVA_SRC}/CMakeLists.txt


RUN mkdir -p ${DIVA_BUILD} && cd ${DIVA_BUILD}
RUN cmake ${DIVA_SRC} -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=${DIVA_INSTALL} \
                    -DDIVA_BUILD_WITH_CUDA=ON -DDIVA_BUILD_WITH_CUDNN=ON \
                    -DDIVA_SUPERBUILD=ON
RUN make -j8

# clean up
RUN rm -rf ${DIVA_SRC}
RUN rm -rf ${DIVA_BUILD}


# Setup_kwiver env variables
ENV VG_PLUGIN_PATH=${DIVA_INSTALL}
ENV PATH=${DIVA_INSTALL}/bin:${PATH}
ENV LD_LIBRARY_PATH=${DIVA_INSTALL}/lib:${LD_LIBRARY_PATH}
ENV KWIVER_PLUGIN_PATH=${DIVA_INSTALL}/lib/kwiver/modules:${DIVA_INSTALL}/lib/kwiver/processes:${KWIVER_PLUGIN_PATH}
# Append here
ENV VITAL_LOGGER_FACTORY=${DIVA_INSTALL}/lib/kwiver/modules/vital_log4cplus_logger
ENV LOG4CPLUS_CONFIGURATION=${DIVA_INSTALL}/log4cplus.properties
# Python environment
ENV PYTHON_LIBRARY="/usr/lib/x86_64-linux-gnu/libpython2.7.so"
ENV PYTHONPATH=${DIVA_INSTALL}/lib/python2.7/dist-packages:${PYTHONPATH}
ENV PYTHONPATH=${DIVA_INSTALL}/lib/site-packages:${PYTHONPATH}
ENV SPROKIT_PYTHON_MODULES=kwiver.processes

# Setup_diva env variables
ENV PYTHONPATH=${DIVA_INSTALL}/lib:${PYTHONPATH}
ENV KWIVER_PLUGIN_PATH=${DIVA_INSTALL}/lib/diva/processes:${DIVA_INSTALL}/lib/diva/modules:${KWIVER_PLUGIN_PATH}
ENV SPROKIT_PYTHON_MODULES=DIVA.processes:${SPROKIT_PYTHON_MODULES}
