class Property < ActiveRecord::Base
  has_many :owner_properties
  has_many :owners, through: :owner_properties

  has_many :complaint311s
  has_many :dob_permits
  has_many :dob_violations
  has_many :hpd_complaints
  has_many :hpd_violations
  has_many :litigations

  def full_address
    "#{self.street_address}, #{self.city}, #{self.state} #{self.zipcode}"
  end
end
