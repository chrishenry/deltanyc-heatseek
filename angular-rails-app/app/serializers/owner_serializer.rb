class OwnerSerializer < ActiveModel::Serializer
  attributes :id, :name, :address_line_one, :address_line_two, 
  :city, :state, :zipcode

  has_many :properties, serializer: OwnerPropertiesSerializer
end
