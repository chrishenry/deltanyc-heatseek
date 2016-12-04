class CreateHdpViolations < ActiveRecord::Migration
  def change
    create_table :hdp_violations do |t|
      t.integer :property_id
      t.string :violation_class
      t.datetime :inspection_date
      t.datetime :certified_date
      t.string :order_number
      t.float :novid
      t.string :nov_description
      t.string :current_status
      t.datetime :current_status_date

      t.timestamps null: false
    end
  end
end
