FROM python:2.7

MAINTAINER Chris Henry <henry.christopher@gmail.com>

ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
  apt-get install -yq --no-install-recommends \
  mysql-client \
  wget \
  bzip2 \
  ca-certificates \
  sudo \
  locales \
  vim && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Install Tini
RUN wget --quiet https://github.com/krallin/tini/releases/download/v0.10.0/tini && \
    echo "1361527f39190a7338a0b434bd8c88ff7233ce7b9a4876f3315c22fce7eca1b0 *tini" | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

ENV SHELL /bin/bash
ENV NB_USER root
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8


# Upgrade pip
RUN pip install --upgrade pip

# Add local files as late as possible to avoid cache busting
COPY docker/start.sh /usr/local/bin/
COPY docker/start-notebook.sh /usr/local/bin/
COPY docker/start-singleuser.sh /usr/local/bin/
COPY docker/jupyter_notebook_config.py /root/.jupyter/
COPY requirements.txt /root/requirements.txt

RUN pip --no-cache-dir install -r /root/requirements.txt

EXPOSE 8888
WORKDIR /root/work

# Configure container startup
ENTRYPOINT ["tini", "--"]
CMD ["start-notebook.sh"]
