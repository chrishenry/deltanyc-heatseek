class AddIndexToHpdComplaints < ActiveRecord::Migration
  def change
    add_index :hpd_complaints, :complaint_id, :unique => true
  end
end
