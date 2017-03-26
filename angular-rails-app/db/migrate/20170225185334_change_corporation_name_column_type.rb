class ChangeCorporationNameColumnType < ActiveRecord::Migration
  def change
    change_column :owners, :corporation_name, :string
  end
end
