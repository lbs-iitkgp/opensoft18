FROM python:3.6

RUN apt-get update

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
	qt5-default \
	libvtk6-dev \ 
	zlib1g-dev \
        yasm \
        libswscale-dev \
        libtbb2 \
        libtbb-dev \
        libavformat-dev \
        libpq-dev

WORKDIR /
ENV OPENCV_VERSION="3.4.1"
RUN wget https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.zip \
&& unzip ${OPENCV_VERSION}.zip \
&& mkdir /opencv-${OPENCV_VERSION}/cmake_binary \
&& cd /opencv-${OPENCV_VERSION}/cmake_binary \
&& cmake -DBUILD_TIFF=ON \
  -DBUILD_opencv_java=OFF \
  -DWITH_CUDA=OFF \
  -DENABLE_AVX=ON \
  -DWITH_OPENGL=ON \
  -DWITH_OPENCL=ON \
  -DWITH_IPP=ON \
  -DWITH_TBB=ON \
  -DWITH_EIGEN=ON \
  -DWITH_V4L=ON \
  -DBUILD_TESTS=OFF \
  -DBUILD_PERF_TESTS=OFF \
  -DCMAKE_BUILD_TYPE=RELEASE \
  -DCMAKE_INSTALL_PREFIX=$(python3.6 -c "import sys; print(sys.prefix)") \
  -DPYTHON_EXECUTABLE=$(which python3.6) \
  -DPYTHON_INCLUDE_DIR=$(python3.6 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
  -DPYTHON_PACKAGES_PATH=$(python3.6 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") .. \
&& make install \
&& rm /${OPENCV_VERSION}.zip \
&& rm -r /opencv-${OPENCV_VERSION}


# Create backend directory
RUN mkdir /backend
COPY . /backend

RUN pip3 install -r "/backend/requirements.txt"
RUN python3 -m spacy download en

# setting environment variables
ENV GOOGLE_APPLICATION_CREDENTIALS="/backend/.gcloud_key.json"
ENV LEXIGRAM_KEY="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJhdSI6Imx4ZzphcGkiLCJzYyI6WyJrZzpyZWFkIiwiZXh0cmFjdGlvbjpyZWFkIl0sImFpIjoiYXBpOjcxMjIwZjAwLTkxMjAtMWZlMC0xYTJkLTk2MWJlOGNkM2Y2MSIsInVpIjoidXNlcjoxNWJlOGE5Yy0zZDAzLTJmNmMtZjkzMS04NjE5Yjk0YzhiOGMiLCJpYXQiOjE1MjIzMDk5MDd9.FxTChifr8ARvp55Xb8Gf1odMZKfrUPueEcmOGL0Fsn8"

CMD ["python3","app.py"]
