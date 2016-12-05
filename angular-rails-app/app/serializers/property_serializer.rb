class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode,
  :total_units, :borough, :block, :lot, :bin, :rent_stabilized, :owner_id

end
