class DobPermitsController < ApplicationController

  def index 
    if params[:property_id]
      @dob_permits = DobPermit.where(
        :property_id => params[:property_id]).paginate(:page => params[:page])
    end
    @dob_permits ||= DobPermit.paginate(:page => params[:page])
    render json: @dob_permits, status: 200   
  end
end