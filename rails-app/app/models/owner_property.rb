class OwnerProperty < ActiveRecord::Base
  belongs_to :owner 
  belongs_to :property
end
