class OwnerPropertiesSerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode, 
  :total_units, :bbl, :bin, :rent_stabilized, :full_address

  belongs_to :owner 
end
