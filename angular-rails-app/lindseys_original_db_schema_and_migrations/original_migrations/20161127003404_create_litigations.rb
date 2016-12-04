class CreateLitigations < ActiveRecord::Migration
  def change
    create_table :litigations do |t|
      t.string :case_type
      t.boolean :case_judgement
      t.integer :property_id

      t.timestamps null: false
    end
  end
end
