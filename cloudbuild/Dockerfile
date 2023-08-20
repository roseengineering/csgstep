FROM continuumio/miniconda3
WORKDIR /data
ADD cloudbuild/requirements.txt .
ADD test_csgstep.py .
ADD csgstep csgstep
ADD setup.py .
RUN conda install -c conda-forge --file requirements.txt
RUN pip install .
