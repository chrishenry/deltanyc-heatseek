class AddUniqueIndexToDobViolations < ActiveRecord::Migration
  def change
    add_index :dob_violations, :isn_dob_bis_viol, :unique => true
  end
end
