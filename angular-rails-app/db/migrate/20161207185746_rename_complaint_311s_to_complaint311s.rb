class RenameComplaint311sToComplaint311s < ActiveRecord::Migration
  def change
    rename_table :complaint_311s, :complaint311s
  end
end
