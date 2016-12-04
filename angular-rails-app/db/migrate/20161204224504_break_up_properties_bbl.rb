class BreakUpPropertiesBbl < ActiveRecord::Migration
  def change
    remove_column :properties, :bbl
    add_column :properties, :borough, :string
    add_column :properties, :block, :integer
    add_column :properties, :lot, :integer
  end
end
