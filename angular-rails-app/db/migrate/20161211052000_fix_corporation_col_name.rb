class FixCorporationColName < ActiveRecord::Migration
  def change
    rename_column :owners, :corpotation_name, :corporation_name
  end
end
