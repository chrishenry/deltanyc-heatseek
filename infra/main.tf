provider "digitalocean" {
  # You need to set this in your .bashrc
  # export DIGITALOCEAN_TOKEN="Your API TOKEN"
  #
}

resource "digitalocean_droplet" "delta_droplet_a" {
  # ID of the `delta-team` SSH key
  ssh_keys           = [8187378]
  image              = "ubuntu-16-10-x64"
  region             = "nyc1"
  size               = "4gb"
  private_networking = true
  backups            = true
  name               = "delta_lookup_tool_a"
  user_data          = "${file("user-data.yml")}"
}
