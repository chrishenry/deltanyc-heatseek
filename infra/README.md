# DeltaNYC Infrastructure

Infrastructure is maintained using;

* [Terraform](https://www.terraform.io/)
* [Cloud-Init](http://cloudinit.readthedocs.io/en/latest/index.html)


# To the droplet's ip address

```bash
$ curl -s -X GET -H "Content-Type: application/json" -H "Authorization: Bearer $DIGITALOCEAN_TOKEN" "https://api.digitalocean.com/v2/droplets" | jq '.[] | .[] | select(.name=="delta_lookup_tool") | .networks.v4 | .[]'
```

We're currently using the DO ubuntu image, which allows ssh directly to the root account.

```bash
ssh -i ~/.ssh/id_rsa_delta root@{public_id}
```

The key to the machine is maintained by Chris Henry


# Configuration

### Google Maps API Key.

The key in use was generated from Chris Henry's Google API Console, but any key
with Google Maps permissions can be used.

# Setup steps

We should be using luigid, but I can't quite figure out what it's supposed to be
doing.

Run the data imports

```bash
$ docker-compose exec nb /bin/bash
$ for f in `ls | grep import | grep .py | grep -v pyc`; do python $f; done
```

Setup the rails app

```bash
$ docker-compose exec web /bin/bash
$ rake db:setup
$ rake db_connector:properties
$ rake db_connector:owners
$ rake db_connector:dob_permits
$ rake db_connector:dob_violations
$ rake db_connector:hpd_complaints
$ rake db_connector:hpd_litigations
$ rake db_connector:three11
```
