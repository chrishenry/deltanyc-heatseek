class AddFieldsToDobViolations < ActiveRecord::Migration
  def change
    add_column :dob_violations, :isn_dob_bis_viol, :string, :unique => true
    add_column :dob_violations, :violation_category, :string
    add_column :dob_violations, :issue_date, :datetime
    add_column :dob_violations, :disposition_date, :datetime
    add_column :dob_violations, :disposition_comments, :string
  end
end
