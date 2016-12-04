class BreakUpPropertiesBbl < ActiveRecord::Migration
  def change
    remove_column :properties, :bbl, :string
    add_column :properties, :borough, :string
    add_column :properties, :block, :integer
    add_column :properties, :lot, :integer
    add_index :properties, [:borough, :block, :lot], :unique => true
  end
end
