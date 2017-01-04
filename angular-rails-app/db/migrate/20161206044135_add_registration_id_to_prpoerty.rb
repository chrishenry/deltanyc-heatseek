class AddRegistrationIdToPrpoerty < ActiveRecord::Migration
  def change
    add_column :properties, :hpd_registration_id, :integer
  end
end
