class HpdComplaintsController < ApplicationController

  def index 
    if params[:property_id]
      @hpd_complaints = HpdComplaint.where(
        :property_id => params[:property_id]).paginate(:page => params[:page])
    end
    @hpd_complaints ||= HpdComplaint.paginate(:page => params[:page])
    render json: @hpd_complaints, status: 200   
  end
end