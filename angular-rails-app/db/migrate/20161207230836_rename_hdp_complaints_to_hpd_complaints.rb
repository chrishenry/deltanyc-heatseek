class RenameHdpComplaintsToHpdComplaints < ActiveRecord::Migration
  def change
    rename_table :hdp_complaints, :hpd_complaints
  end
end
