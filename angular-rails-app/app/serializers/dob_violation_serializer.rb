class DobViolationSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :violation_type, :violation_type,
  :violation_category, :issue_date, :disposition_date, :disposition_comments

  belongs_to :property
end






