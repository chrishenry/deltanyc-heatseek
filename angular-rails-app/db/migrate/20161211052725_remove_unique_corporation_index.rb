class RemoveUniqueCorporationIndex < ActiveRecord::Migration
  def change
    remove_index :owners, :hpd_registration_id
  end
end
