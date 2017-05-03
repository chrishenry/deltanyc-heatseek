class HpdComplaintSerializer < ActiveModel::Serializer
  attributes :id, :property_id, :status, :status_date, :status_id, :complaint_id,
  :apartment, :major_category, :minor_category, :code, :received_date, :complaint_type

  def received_date
    object.received_date&.strftime('%m/%d/%Y')
  end

  def status_date
    object.status_date&.strftime('%m/%d/%Y')
  end

end

