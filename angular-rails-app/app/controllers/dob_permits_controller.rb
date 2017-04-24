class DobPermitsController < ApplicationController

  def index 
    if params[:property_id]
      @dob_permits = DobPermit.where(
        :property_id => params[:property_id]).paginate(:page => params[:page]).order(expiration_date: :desc)
    end
    @dob_permits ||= DobPermit.paginate(:page => params[:page])
    render json: @dob_permits, adapter: :json, 
      meta: meta_attributes(@dob_permits), status: 200   
  end
end