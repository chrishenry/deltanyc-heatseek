class Property < ActiveRecord::Base
  has_many :owner_properties
  has_many :owners, through: :owner_properties
end
