class Owner < ActiveRecord::Base
  has_many :owner_properties
  has_many :properties, through: :owner_properties

  def full_identity
    if self.corporation_name
      "#{self.name} | #{self.corporation_name}"
    else
      "#{self.name}" 
    end 
  end

end
