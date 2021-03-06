# original source - https://github.com/jupyter/docker-stacks/blob/master/minimal-notebook/Dockerfile

ARG BASE_CONTAINER=jupyter/minimal-notebook:python-3.8.8
FROM $BASE_CONTAINER

USER root

# Install all OS dependencies for fully functional notebook server
RUN apt-get update && apt-get install -yq --no-install-recommends \
    vim

# allow mercury which runs on port 5000 to embed jupyter notebook
RUN echo 'c.NotebookApp.tornado_settings = { \
    "headers": { \
    "Content-Security-Policy": "frame-ancestors 'self' http://localhost:5000", \
    "Access-Control-Allow-Origin": "http://locahost:5000", \
    } \
    }' >> /home/jovyan/.jupyter/jupyter_notebook_config.py

# copy container src code and install dependecies
RUN pip3 install supervisor
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Add mercury nb extension
ARG NBEXTENSIONS_DIR="/opt/conda/lib/python3.8/site-packages/jupyter_contrib_nbextensions/nbextensions/"
RUN pip3 install jupyter_contrib_nbextensions
COPY nbextensions/mercury_eventlistener $NBEXTENSIONS_DIR/mercury_eventlistener
RUN ls $NBEXTENSIONS_DIR

RUN jupyter contrib nbextensions install
RUN jupyter nbextension enable mercury_eventlistener/main

COPY container/ container/

# create an empty untitled.ipynb
RUN mkdir work/scripts/
RUN ls
RUN python3 -m container.cli create-notebook --name Untitled.ipynb

RUN ls work/scripts/

ADD supervisord.conf /etc/supervisor/supervisord.conf 

RUN ls /etc/supervisor

ENTRYPOINT ["/opt/conda/bin/supervisord"]
# remove all token based access to notebooks
#CMD ["jupyter", "notebook", "--allow-root", "--no-browser","--NotebookApp.token=''","--NotebookApp.password=''"]



# Switch back to jovyan to avoid accidental container runs as root
# USER $NB_UID
