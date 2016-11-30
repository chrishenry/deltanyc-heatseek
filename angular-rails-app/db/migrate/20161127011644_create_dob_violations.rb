class CreateDobViolations < ActiveRecord::Migration
  def change
    create_table :dob_violations do |t|
      t.integer :property_id
      t.string :type

      t.timestamps null: false
    end
  end
end
