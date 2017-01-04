class AddFieldsToHpdComplaintss < ActiveRecord::Migration
  def change
    add_column :hpd_complaints, :received_date, :datetime
    add_column :hpd_complaints, :complaint_id, :integer
    add_column :hpd_complaints, :apartment, :string
  end
end
