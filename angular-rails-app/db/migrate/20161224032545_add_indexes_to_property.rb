class AddIndexesToProperty < ActiveRecord::Migration
  def change
    add_index :properties, [:street_address, :zipcode]
  end
end
