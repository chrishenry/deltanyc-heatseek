class HpdComplaintsController < ApplicationController

  def index 
    if params[:property_id]
      @hpd_complaints = HpdComplaint.where(
        :property_id => params[:property_id]).paginate(:page => params[:page]).order(status: :desc)
    end
    @hpd_complaints ||= HpdComplaint.paginate(:page => params[:page])
    render json: @hpd_complaints, adapter: :json, 
    meta: meta_attributes(@hpd_complaints), status: 200   
  end
end