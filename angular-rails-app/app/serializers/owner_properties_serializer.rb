class OwnerPropertiesSerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode,
  :total_units, :expand_borough, :block, :lot, :bin, :bin, :rent_stabilized, :full_address

  belongs_to :owner
end
