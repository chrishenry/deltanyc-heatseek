class LitigationsController < ApplicationController
  
  def index 
    if params[:property_id]
      @litigations = Litigation.where(
        :property_id => params[:property_id]).paginate(:page => params[:page])
    end
    @litigations ||= Litigation.paginate(:page => params[:page])
    render json: @litigations, status: 200   
  end
end