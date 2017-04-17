# Heatseek Housing Data Tool

The goals of this repo are:

* Create a dataset comprised of various NYC housing data that will can be used
as the source data to identify and predict bad landlords.
* Provide a way to create reports suitable for sending to lawyers and activists.
* Expose this data via a web app.

## Getting Started

The recommended way to install and run this repo is using Docker.

The simplest way to install Docker is to install [the Platform from the official website](https://www.docker.com/products/docker). The official website offers [a good tutorial](https://docs.docker.com/engine/getstarted/).

Before using any of our Docker images, you'll need to create a .env file. The required fields are listed in .env.example. The defaults are likely good enough for running an instance of the site locally, but you'll need to obtain [an API key for the NYC geoclient](https://developer.cityofnewyork.us/api/geoclient-api) for some of the data cleaning steps to function.

`docker-compose up` will build and install our images, and launch them in containers.  These images are:

* db: The MySQL database storing NYC city data both in semi-raw form and joined into a model for the Rails website. The database can be examined with `docker exec deltanycheatseek_db_1 mysql -u <user from .env> -p <password from .env>`. Local clients can connect at 127.0.0.1:3306 ([localhost will not work](http://stackoverflow.com/a/32361238/103315)).
* db-udf: Installs [user-defined functions for making regular expression queries](https://github.com/mysqludf/lib_mysqludf_preg) required for data-cleaning into MySQL. Only needs to be run once.
* luigid: Runs a [Luigi](http://luigi.readthedocs.io) central scheduler. Tasks are usually started by other containers. You can connect to a web view at localhost:8082.
* luigi-import-worker: Runs all import scripts. Will skip imports already run using this image. Imports can be run in parallel using standard docker methods like `docker-compose scale` (eg. `docker-compose scale luigi-import-worker=4`).
* nb: Installs Python and starts a Jupyter notebook at [localhost:8888](http://localhost:8888).
* web: Installs Ruby on Rails and starts a server at [localhost](http://localhost). Like the data-import scripts, you can conect to a running instance with `docker exec -it deltanycheattseek_web_1 /bin/bash` to run rake tasks. To view a demo of the tool, connect to the instance, then run `rake db:setup`. In the demo, fake data will be provided for "10 West 109th Street".

Once all the images are built and run once, only the nb or web images need to be explicitly lanched via docker-compose (eg. `docker-compose up web`) depending on the type of work you plan to do. Launching either will also launch the db container.

Alternatively, the repo can run without Docker, but the user is responsible for installing all requirements themselves: MySQL, Python, packages specified in requirements.txt, Ruby on Rails, packagese specified in the Gemfile, and nodejs. You'll also need to install [the user-defined functions providing regular expressions for MySQL](https://github.com/mysqludf/lib_mysqludf_preg/blob/testing/INSTALL).

## Data Sources

### 311 Complaint data

Filtered by complaint types described [here](https://docs.google.com/spreadsheets/d/1hJIRu1Ku2pgaKfbFjXLEzN2jNH9rYmUtjpLZZHbfe80/edit).
Includes from: March 14th, 2014
146295 data points

Complaints can be made to 311 and directed to HPD for interior housing maintenance issues (as opposed to exterior and/structural issues which usually get directed to DOB). The Complaints database is part of the NYC Open Data portal, and is updated nightly.


### AEP

Includes from: 2008
1885 datapoints
Not included in web app

The Alternative Enforcement Program (AEP) is an enforcement program which identifies the 200 most distressed multiple dwellings citywide each year. Owners of multiple dwellings can avoid participation in AEP by properly maintaining their building, submitting a current and valid property registration to the Department of Housing Preservation and Development (HPD), and correcting and certifying all HPD violations. The City will let registered owners, managing agents, and tenants know that their building was chosen to be in the program.


### DOB Permits

Includes from: 2013-04-25
648528 data points

A list of permits issued for a particular day and associated data - included in the NYC Open Data. Additionally, prior weekly and monthly reports are archived at DOB and are not available on NYC Open Data.


### DOB Violations

Not sure how far the data goes back, as dates are not formatted correctly.
1144624 data points

Violations stemming from complaints made about poor building conditions, mainly pertaining to the exterior of the building and/or the building’s structural integrity, but also covering complaints having to do with construction. When complaints are made, a DOB inspector is dispatched to the building to validate the complaints and issue violations.


### HPD Buildings

307352 buildings

???

### HPD Complaints

Includes from: 2003-03-20
917522 data points

In addition to calling 311 to make complaints about building conditions, individuals can also call HPD directly to lodge a complaint.

### HPD Registrations

Includes from: 1993-04-01 (This might be earlier, as there's no date telling us when the data was created, only when it was last updated)
162948 data points

Property owners of residential buildings are required by law to register annually with HPD if the property is a multiple dwelling (3+ residential units) or a private dwelling (1-2 residential units) where neither the owner nor the owner's immediate family resides. Ownership information is often found in these registrations.

### Pluto

Includes from: 1984-11-14
858370 data points

Planning and Land Use data. Extensive land use and geographic data at the tax lot level in comma–separated values (CSV) file format. The PLUTO files contain more than seventy fields derived from data maintained by city agencies.

### Rent Stabilization Data

Includes from 2007
45064 data points

Derived from the quarterly tax filings with New York State, where landlords are supposed to list how many rent-stabilized units there are in the building. Allows us to track changes in rent stabilized units over time.

### HPD Litigation Data

Stats for Litigations;
67382 data points
Includes from: 2000-09-11

Cases initiated by HPD against a landlord in Housing Court. Tenant-initiated cases are not included in this data.

## Abbreviations:

**HPD**: NYC Agency, stands for Housing Preservation and Development

**DOB**: NYC Agency, stands for Department of Buildings

**311**: NYC Agency - operates as a call center for all types of information sharing. Information submitted to 311, usually in the form of complaints, gets directed to the appropriate agency for follow up.

**Rent Stabilization**: for a detailed FAQ, see here.
