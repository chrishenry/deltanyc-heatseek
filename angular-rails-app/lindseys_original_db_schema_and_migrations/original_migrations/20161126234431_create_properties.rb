class CreateProperties < ActiveRecord::Migration
  def change
    create_table :properties do |t|
      t.string :street_address
      t.string :city
      t.string :state
      t.string :zipcode
      t.integer :total_units
      t.string :bbl
      t.string :bin
      t.boolean :rent_stabilized
      t.integer :owner_id

      t.timestamps null: false
    end
  end
end
