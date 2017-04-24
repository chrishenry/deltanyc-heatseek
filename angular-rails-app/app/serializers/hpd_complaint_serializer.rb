class HpdComplaintSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :status, :status_date, :status_id, :complaint_id,
  :apartment
end

