class Complaint311sController < ApplicationController

  def index 
    if params[:property_id]
      @complaint311s = Complaint311.where(
        :property_id => params[:property_id]).paginate(:page => params[:page])
    end
    @complaint311s ||= Complaint311.paginate(:page => params[:page])
    render json: @complaint311s, adapter: :json, 
    meta: meta_attributes(@complaint311s), status: 200   
  end
end