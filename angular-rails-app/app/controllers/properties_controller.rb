class PropertiesController < ApplicationController

  before_action :set_property, only: [:show]

  def index
    @properties = Property.paginate(:page => params[:page])
    render json: @properties, status: 200
  end

  def show
    render json: @property, status: 200
  end

  private

  def set_property
    @property = Property.find_by(id: params[:id])
  end

end
