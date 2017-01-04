class RemoveOwnerIdFromProperty < ActiveRecord::Migration
  def change
    remove_column(:properties, :owner_id)
  end
end
