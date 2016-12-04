class Owner < ActiveRecord::Base
  has_many :owner_properties
  has_many :properties, through: :owner_properties
end
