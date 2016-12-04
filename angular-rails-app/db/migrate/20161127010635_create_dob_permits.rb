class CreateDobPermits < ActiveRecord::Migration
  def change
    create_table :dob_permits do |t|
      t.integer :property_id
      t.string :borough
      t.float :bin
      t.float :block
      t.string :lot
      t.string :community_board
      t.string :permit_status
      t.float :permit_sequence_num
      t.datetime :filing_date
      t.datetime :expiration_date

      t.timestamps null: false
    end
  end
end
