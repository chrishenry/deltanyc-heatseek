class AddUniqueKeyToComplaint311 < ActiveRecord::Migration
  def change
    add_column :complaint311s, :unique_key, :integer
    add_index :complaint311s, :unique_key, :unique => true
  end
end
