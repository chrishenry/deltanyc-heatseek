class DobViolationSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :violation_type

  belongs_to :property
end
