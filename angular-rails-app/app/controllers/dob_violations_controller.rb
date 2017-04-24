class DobViolationsController < ApplicationController

  def index 
    if params[:property_id]
      @dob_violations = DobViolation.where(
        :property_id => params[:property_id]).paginate(:page => params[:page]).order(issue_date: :desc)
    end
    @dob_violations ||= DobViolation.paginate(:page => params[:page])
    render json: @dob_violations, adapter: :json, 
      meta: meta_attributes(@dob_violations), status: 200   
  end
end