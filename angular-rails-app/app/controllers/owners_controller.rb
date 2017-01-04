class OwnersController < ApplicationController

   before_action :set_owner, only: [:show]

  def index
    @owners = Owner.all
    render json: @owners, status: 200
  end

  def show
    render json: @owner, status: 200
  end

  private

  def set_owner
    @owner = Owner.find_by(id: params[:id])
  end

end
