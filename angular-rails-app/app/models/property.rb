class Property < ActiveRecord::Base
  has_many :owner_properties
  has_many :owners, through: :owner_properties

  has_many :complaint311s
  has_many :dob_permits
  has_many :dob_violations
  has_many :hpd_complaints
  has_many :hpd_violations
  has_many :litigations

  @boros = {
    'MN' => 'MANHATTAN',
    'BK' => 'BROOKLYN',
    'BX' => 'BRONX',
    'SI' => 'STATEN ISLAND',
    'QN' => 'QUEENS',
  }

  def full_address
    "#{self.street_address}, #{self.city}, #{self.state} #{self.zipcode}"
  end

  def self.full_borough
    x = self.read_attribute(:borough)
    @boros[x]
  end

  def expand_borough
    boros = {
      'MN' => 'MANHATTAN',
      'BK' => 'BROOKLYN',
      'BX' => 'BRONX',
      'SI' => 'STATEN ISLAND',
      'QN' => 'QUEENS',
    }
    boros[self.borough]
  end

end
