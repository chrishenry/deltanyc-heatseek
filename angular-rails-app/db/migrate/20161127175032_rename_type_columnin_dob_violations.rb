class RenameTypeColumninDobViolations < ActiveRecord::Migration
  def change
    rename_column :dob_violations, :type, :violation_type
  end
end
