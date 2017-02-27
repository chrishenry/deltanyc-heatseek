# Heatseek Housing Data Tool

The goals of this repo are:

* Create a dataset comprised of various NYC housing data that will can be used
as the source data to identify and predict bad landlords.
* Provide a way to create reports suitable for sending to lawyers and activists.
* Expose this data via a web app.

## Getting Started

The recommended way to install and run this repo is using Docker.

The simplest way to install Docker is to install [the Platform from the official website](https://www.docker.com/products/docker). The official website offers [a good tutorial](https://docs.docker.com/engine/getstarted/).

Before launching any of our containers, you'll need to create a .env file. The required fields are listed in .env.example. The defaults are likely good enough for running an instance of the site locally, but you'll need to obtain [an API key for the NYC geoclient](https://developer.cityofnewyork.us/api/geoclient-api) for some of the data cleaning steps to function.

`docker-compose up` will install and launch all our containers.  These containers are:

* db: The MySQL database storing NYC city data both in semi-raw form and joined into a model for the Rails website. The database can be examined with `docker exec deltanycheatseek_db_1 mysql -u <user from .env> -p <password from .env>`. Local clients can connect at 127.0.0.1:3306 ([localhost will not work](http://stackoverflow.com/a/32361238/103315)).
* db-udf: Installs [user-defined functions for making regular expression queries](https://github.com/mysqludf/lib_mysqludf_preg) required for data-cleaning into MySQL. Only needs to be run once.
* nb: Installs Python and starts a Jupyter notebook at [localhost:8888](http://localhost:8888). Can also be used to run the data-import scripts: run `docker exec -it deltanycheatseek_nb_1 /bin/bash`, then execute the scripts
* web: Installs Ruby on Rails and starts a server at [localhost:3000](http://localhost:3000). Like the data-import scripts, you can conect to a running instance with `docker exec -it deltanycheattseek_web_1 /bin/bash` to run rake tasks. To view a demo of the tool, connect to the instance, then run `rake db:setup`. In the demo, fake data will be provided for "10 West 109th Street".

Once everything is installed, only the nb or web containers need to be explicitly lanched (eg. `docker-compose up web`) depending on the type of work you plan to do. Launching either will also launch the db container.

Alternatively, the repo can run without Docker, but the user is responsible for installing all requirements themselves: MySQL, Python, packages specified in requirements.txt, Ruby on Rails, packagese specified in the Gemfile, and nodejs. You'll also need to install [the user-defined functions providing regular expressions for MySQL](https://github.com/mysqludf/lib_mysqludf_preg/blob/testing/INSTALL).

Data Conventions
***************************
Borough (Boro) should be shortened to a 2 letter wherever stored.
