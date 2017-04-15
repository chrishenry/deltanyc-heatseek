class HpdViolationsController < ApplicationController

  def index 
    if params[:property_id]
      @hpd_violations = HpdViolation.where(
        :property_id => params[:property_id]).paginate(:page => params[:page])
    end
    @hpd_violations ||= HpdViolation.paginate(:page => params[:page])
    render json: @hpd_violations, adapter: :json, 
      meta: meta_attributes(@hpd_violations), status: 200   
  end
end