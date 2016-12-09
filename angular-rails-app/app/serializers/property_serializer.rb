class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode, 
  :total_units, :bbl, :bin, :rent_stabilized, :owner_id, :full_address

  has_many :dob_permits
  has_many :dob_violations
  has_many :hpd_violations
  has_many :hpd_complaints
  has_many :litigations
  has_many :complaint311s
  has_many :owners

end
