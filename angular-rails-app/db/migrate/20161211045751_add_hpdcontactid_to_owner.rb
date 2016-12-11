class AddHpdcontactidToOwner < ActiveRecord::Migration
  def change
    add_column :owners, :corpotation_name, :integer
    add_column :owners, :hpd_registration_id, :integer
    add_column :owners, :hpd_registration_contact_id, :integer
    add_column :owners, :hpd_type, :string
    add_index :owners, :hpd_registration_id, :unique => true
    add_index :owners, :hpd_registration_contact_id, :unique => true
  end
end
