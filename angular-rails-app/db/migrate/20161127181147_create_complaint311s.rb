class CreateComplaint311s < ActiveRecord::Migration
  def change
    create_table :complaint_311s do |t|
      t.integer :property_id
      t.datetime :created_date
      t.datetime :closed_date
      t.string :agency
      t.string :complaint_type
      t.string :status
      t.datetime :due_date
      t.string :resolution_description

      t.timestamps null: false
    end
  end
end

