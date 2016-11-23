DELTA NYC COHORT 2
***************************

This repo is intended as the deliverable for Civic Hall Labs' Delta NYC team
focused on Heat Seek.

The goals are;

* Create a dataset comprised of various NYC housing data that will can be used
as the source data to identify and predict bad landlords.
* Provide a way to create reports suitable for sending to lawyers and activists.
* Expose this data via a web app.


Python Notebooks
***************************

As we are committing full Python notebooks, be sure to clear output before
saving. (`Cell` -> `All Output` -> `Clear`). This will help us keep diffs clean
as we work.


Getting Started
***************************

There are two options for getting started with this repo.

The first is to install the Python packages and run Jupyter.

TODO: Needs better documentation.

The second is to use docker;

* [Install Docker and docker-compose](https://docs.docker.com/engine/getstarted/)
* Run `cp .env.example .env`
* Run `docker-compose up`
* The Jupyter notebook will be running at `docker-machine ip {name}`:8888

This method will use an .env file to configure the containers.






