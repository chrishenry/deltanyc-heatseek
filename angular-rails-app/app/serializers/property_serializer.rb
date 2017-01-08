class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode,
  :total_units, :expand_borough, :block, :lot, :bin, :rent_stabilized, :full_address,
  :hpd_open_complaints_count, :dob_permits_count, :dob_violations_count, :litigations_count,
  :complaint311s_count

  has_many :hpd_violations
  has_many :owners


  def complaint311s_count
    @object.complaint311s.size
  end

  def litigations_count
    @object.hpd_complaints.size
  end

  def hpd_open_complaints_count
    @object.hpd_complaints.where(status: 'OPEN').size
  end

  def dob_permits_count
    @object.dob_permits.size
  end

  def dob_violations_count
    @object.dob_violations.size
  end

  has_many :litigations do
    @object.litigations.limit(5)
  end

  has_many :dob_violations do
    @object.dob_violations.limit(5)
  end

  has_many :dob_permits do
    @object.dob_permits.limit(5)
  end

  has_many :complaint311s do
    @object.complaint311s.limit(5)
  end

  has_many :hpd_complaints do
    @object.hpd_complaints.where(status: 'OPEN').limit(5)
  end

end
