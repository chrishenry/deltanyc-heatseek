class HpdViolationSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :violation_class, :inspection_date,
  :certified_date, :order_number, :novid, :nov_description, :current_status,
  :current_status_date
end

