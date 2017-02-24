class ChangeCorporationNameTypeInOwners < ActiveRecord::Migration
  def self.up
    change_column :owners, :corporation_name, :string
  end
 
  def self.down
    change_column :owners, :corporation_name, :integer
  end
end
