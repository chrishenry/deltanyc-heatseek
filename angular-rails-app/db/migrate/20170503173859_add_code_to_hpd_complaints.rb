class AddCodeToHpdComplaints < ActiveRecord::Migration
  def change
    add_column :hpd_complaints, :code, :string
  end
end
