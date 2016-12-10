class Complaint311Serializer < ActiveModel::Serializer
  attributes :id, :created_date, :closed_date, :agency, :complaint_type,
  :status, :due_date, :resolution_description
end

 