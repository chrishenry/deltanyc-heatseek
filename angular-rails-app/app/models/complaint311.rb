class Complaint311 < ActiveRecord::Base
  belongs_to :property

  # There are ~240 categories. We def don't care about all of them
  # This is just a guess as to what we *do* care about. 
	Categories = [
	  "Maintenance or Facility",
	  "HEATING",
	  "Building/Use",
	  "APPLIANCE",
	  "BEST/Site Safety",
	  "Indoor Air Quality",
	  "Air Quality",
	  "Weatherization",
	  "Water Quality",
	  "Indoor Sewage",
	  "Boilers",
	  "Mold",
	  "UNSANITARY CONDITION",
	  "WATER LEAK",
	  "HEAT/HOT WATER",
	  "Standing Water",
	  "Rodent",
	  "Indoor Sewage",
	  "Emergency Response Team (ERT)",
	  "Lead",
	  "Eviction",
	]

end
