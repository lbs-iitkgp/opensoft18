FROM ubuntu:16.04

ENV http_proxy http://172.16.2.30:8080
ENV https_proxy https://172.16.2.30:8080

RUN apt-get update \
&& apt-get install -y \
	wget \
	curl \
	git \
	unzip \
	cmake \
	build-essential \
	sudo \
	mesa-utils \
	apt-transport-https ca-certificates \
	python3-pip \
	pkg-config \
	python-dev \ 
	python-opencv \ 
	libopencv-dev \ 
	libav-tools  \ 
	libjpeg-dev \ 
	libpng-dev \ 
	libtiff-dev \ 
	libjasper-dev \ 
	libgtk2.0-dev \ 
	python-numpy \ 
	python-pycurl \ 
	libatlas-base-dev \
	gfortran \
	webp \ 
	python-opencv \ 
	qt5-default \
	libvtk6-dev \ 
	zlib1g-dev \
	&& apt-get clean

RUN mkdir -p ~/opencv cd ~/opencv && \
    wget https://github.com/Itseez/opencv/archive/3.0.0.zip && \
    unzip 3.0.0.zip && \
    rm 3.0.0.zip && \
    mv opencv-3.0.0 OpenCV && \
    cd OpenCV && \
    mkdir build && \ 
    cd build && \
    cmake \
    -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local .. && \
#    -DWITH_QT=ON \ 
#    -DWITH_OPENGL=ON \ 
#    -DFORCE_VTK=ON \
#    -DWITH_TBB=ON \
#    -DWITH_GDAL=ON \
#    -DWITH_XINE=ON \
#    -DBUILD_EXAMPLES=ON .. && \
    make -j4 && \
    make install && \ 
    ldconfig


# Create directory
RUN mkdir /backend
COPY . /backend

WORKDIR /backend
RUN sudo -H pip3 install --upgrade pip \
&& sudo -H pip3 install -r requirements.txt \
&& apt-get clean \
GOOGLE_APPLICATION_CREDENTIALS="/home/prashant01/Desktop/opensoft18/backend/opensoft-196212a7ecf7.json"



CMD ["python3","app.py"]