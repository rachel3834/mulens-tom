FROM centos:7

EXPOSE 80
ENTRYPOINT [ "/init" ]

# install packages
RUN yum -y install epel-release \
        && yum -y install nginx python-pip supervisor python-devel uwsgi-plugin-python \
        && yum -y install gcc g++ gcc-gfortran \
        && yum -y update \
        && yum -y clean all

# system configuration
COPY docker/ /

# install python requirements
COPY pip-requirements.txt /var/www/spitzermicrolensing/
RUN pip install --upgrade pip \
        && pip install numpy \
        && pip install -r /var/www/spitzermicrolensing/pip-requirements.txt \
        && rm -rf ~/.cache ~/.pip

# copy application
COPY . /var/www/spitzermicrolensing/
