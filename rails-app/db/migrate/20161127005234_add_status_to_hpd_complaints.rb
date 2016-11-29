class AddStatusToHpdComplaints < ActiveRecord::Migration
  def change
    add_column :hdp_complaints, :status, :string
    add_column :hdp_complaints, :status_date, :datetime
    add_column :hdp_complaints, :status_id, :integer
  end
end
