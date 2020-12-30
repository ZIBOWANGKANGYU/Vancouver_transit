FROM python:3.8-buster

RUN wget --quiet https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh -O ~/anaconda.sh && \
    /bin/bash ~/anaconda.sh -b -p /opt/conda && \
    rm ~/anaconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
    echo "conda activate base" >> ~/.bashrc && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete && \
    /opt/conda/bin/conda clean -afy && \
    /opt/conda/bin/conda update -n base -c defaults conda

ENV PATH="/opt/conda/bin:${PATH}"

# install docopt python package
RUN conda update conda

RUN conda install -y -c anaconda \ 
    docopt \
    requests

RUN pip install -Iv altair==4.1.0
RUN pip install -Iv contextily==1.0.0
RUN pip install -Iv dbfread==2.0.7
RUN pip install -Iv geopandas==0.8.1
RUN pip install -Iv matplotlib==3.3.1
RUN pip install -Iv numpy==1.19.1
RUN pip install -Iv pandas==1.1.1
RUN pip install -Iv scikit-learn==0.23.2
RUN pip install -Iv shap==0.37.0
RUN pip install -Iv shapely==1.7.1
RUN pip install -Iv tabulate==0.8.7

RUN conda install -y -c conda-forge feather-format

RUN conda install -c conda-forge altair_saver