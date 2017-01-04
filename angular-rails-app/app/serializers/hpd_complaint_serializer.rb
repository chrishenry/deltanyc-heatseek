class HpdComplaintSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :complaint_type, :major_category_id, :minor_category_id,
  :code_id, :status, :status_date, :status_id

  belongs_to :property
end

