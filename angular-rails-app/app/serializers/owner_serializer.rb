class OwnerSerializer < ActiveModel::Serializer
  attributes :id, :name, :address_line_one, :address_line_two, 
  :city, :state, :zipcode, :full_identity

  has_many :properties, serializer: OwnerPropertiesSerializer

  def name
    object.name.blank? ? object.corporation_name : object.name
  end

end
