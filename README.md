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

The first is to install the Python packages and run Jupyter. Ditto for the rails
app.

TODO: Needs better documentation.

The second is to use docker;

* [Install Docker and docker-compose](https://docs.docker.com/engine/getstarted/)
* Run `cp .env.example .env`
* Run `docker-compose up`
* The Jupyter notebook will be running at [localhost:8888](http://localhost:8888)
* The Rails app will be running at [localhost:3000](http://localhost:3000)

This method will use an .env file to configure the containers.


To get into the web container, and run rake tasks, etc;

```bash
docker-compose exec web /bin/bash
```

To examine MySQL directly you can use docker-compose to exec the mysql client;

```bash
docker-compose exec db mysql -u deltanyc -ppassword deltanyc
```

OR you can connect to container over 3306 using the local mysql client if you
have it installed. See [this article](http://stackoverflow.com/a/32361238/103315)
on why you need to use `127.0.0.1`.

```bash
mysql -h 127.0.0.1 -P 3306 -u deltanyc -ppassword
```
