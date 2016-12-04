class Property < ActiveRecord::Base
  has_many :owner_properties
  has_many :owners, through: :owner_properties

  has_many :complaint_311s
  has_many :dob_permits
  has_many :dob_violations
  has_many :hdp_complaints
  has_many :hdp_violations
  has_many :litigations
end
