class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode,
  :total_units, :expand_borough, :block, :lot, :bin, :rent_stabilized, :full_address,
  :hpd_open_complaints_count

  has_many :dob_permits
  has_many :dob_violations
  has_many :hpd_violations
  has_many :litigations
  has_many :owners

  def hpd_open_complaints_count
    @object.hpd_complaints.where(status: 'OPEN').size
  end

  has_many :complaint311s do
    @object.complaint311s.limit(5)
  end

  has_many :hpd_complaints do
    @object.hpd_complaints.where(status: 'OPEN').limit(5)
  end

end
