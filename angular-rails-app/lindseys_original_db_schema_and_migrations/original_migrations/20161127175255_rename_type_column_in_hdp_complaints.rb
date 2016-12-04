class RenameTypeColumnInHdpComplaints < ActiveRecord::Migration
  def change
    rename_column :hdp_complaints, :type, :complaint_type
  end
end
