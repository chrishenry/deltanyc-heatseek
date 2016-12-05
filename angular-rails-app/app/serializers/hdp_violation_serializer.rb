class HdpViolationSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :violation_class, :inspection_date,
  :certified_date, :order_number, :novid, :nov_description, :current_status,
  :current_status_date

  belongs_to :property
end

