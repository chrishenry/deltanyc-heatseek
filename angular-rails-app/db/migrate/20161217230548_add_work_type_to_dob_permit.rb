class AddWorkTypeToDobPermit < ActiveRecord::Migration
  def change
    add_column :dob_permits, :work_type, :string
  end
end
