provider "digitalocean" {
  # You need to set this in your .bashrc
  # export DIGITALOCEAN_TOKEN="Your API TOKEN"
  #
}

resource "digitalocean_droplet" "delta_droplet" {
  ssh_keys           = [8187378]
  image              = "ubuntu-16-10-x64"
  region             = "nyc1"
  size               = "4gb"
  private_networking = true
  backups            = true
  name               = "delta_lookup_tool"
  user_data          = "${file("user-data.yml")}"
}
