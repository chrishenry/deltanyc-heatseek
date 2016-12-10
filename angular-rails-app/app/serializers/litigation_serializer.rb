class LitigationSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :case_type, :case_judgement

  belongs_to :property
end