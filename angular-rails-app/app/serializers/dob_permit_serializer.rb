class DobPermitSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :borough, :bin, :block, :lot,
  :permit_status, :filing_date, :expiration_date, :work_type

  belongs_to :property 
end

 