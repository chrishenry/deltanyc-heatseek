class CreateHdpComplaints < ActiveRecord::Migration
  def change
    create_table :hdp_complaints do |t|
      t.string :type
      t.integer :major_category_id
      t.integer :minor_category_id
      t.integer :code_id
      t.integer :property_id

      t.timestamps null: false
    end
  end
end
