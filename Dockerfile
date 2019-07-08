FROM jupyter/scipy-notebook

RUN conda install -c conda-forge rise

RUN git clone https://github.com/damianavila/RISE.git && \
  cd RISE && \
  git checkout tags/5.6.0.dev3 -b rise_install && \
  npm install && \
  npm run build && \
  pip install . && \
  jupyter-nbextension install rise --py --sys-prefix --symlink && \
  jupyter-nbextension enable rise --py --sys-prefix && \
  export NODE_OPTIONS=--max-old-space-size=4096 && \
  jupyter labextension install @jupyter-widgets/jupyterlab-manager --no-build && \
  jupyter labextension install plotlywidget --no-build && \
  jupyter labextension install @jupyterlab/plotly-extension --no-build && \
  jupyter labextension install jupyterlab-chart-editor --no-build && \
  jupyter lab build && \
  unset NODE_OPTIONS

RUN pip install plotly_express ipywidgets==7.5.0
RUN pip install webcolors