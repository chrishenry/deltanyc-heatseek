class AddProblemFieldsToHpdComplaints < ActiveRecord::Migration
  def change
    add_column :hpd_complaints, :major_category, :string
    add_column :hpd_complaints, :minor_category, :string
    add_column :hpd_complaints, :description, :string
  end
end
