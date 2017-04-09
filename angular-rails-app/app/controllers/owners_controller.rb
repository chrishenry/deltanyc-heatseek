class OwnersController < ApplicationController

   before_action :set_owner, only: [:show]

  def index
    if params[:name]       
      @owners = Owner.where('name LIKE :input OR corporation_name LIKE :input ', input: "%#{params[:name]}%").limit(6)
    else
      @owners = Owner.paginate(:page => params[:page])
    end
    render json: @owners, adapter: :json, 
    meta: meta_attributes(@owners),status: 200
  end


  def show
    render json: @owner, status: 200
  end

  private

  def set_owner
    @owner = Owner.find_by(id: params[:id])
  end

end
