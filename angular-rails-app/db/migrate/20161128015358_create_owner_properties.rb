class CreateOwnerProperties < ActiveRecord::Migration
  def change
    create_table :owner_properties do |t|
      t.integer :property_id
      t.integer :owner_id

      t.timestamps null: false
    end
  end
end
