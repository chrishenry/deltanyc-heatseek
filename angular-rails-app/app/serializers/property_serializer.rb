class PropertySerializer < ActiveModel::Serializer
  attributes :id, :street_address, :city, :state, :zipcode,
  :total_units, :expand_borough, :block, :lot, :bin, :rent_stabilized, :full_address,
  :hpd_open_complaints_count, :hpd_complaints_count, :dob_permits_count, :dob_violations_count, :litigations_count,
  :complaint311s_count, :hpd_violations_count

  has_many :owners


  def complaint311s_count
    @object.complaint311s.size
  end

  def litigations_count
    @object.litigations.size
  end

  def hpd_open_complaints_count
    @object.hpd_complaints.where(status: 'OPEN').size
  end

  def hpd_complaints_count
    @object.hpd_complaints.size
  end

  def hpd_violations_count
    @object.hpd_violations.size
  end

  def dob_permits_count
    @object.dob_permits.size
  end

  def dob_violations_count
    @object.dob_violations.size
  end
end
