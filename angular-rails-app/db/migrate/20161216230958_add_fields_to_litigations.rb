class AddFieldsToLitigations < ActiveRecord::Migration
  def change
    add_column :litigations, :litigation_id, :integer
    add_column :litigations, :case_open_date, :datetime
    add_column :litigations, :case_status, :string
    add_index :litigations, :litigation_id, :unique => true
  end
end
