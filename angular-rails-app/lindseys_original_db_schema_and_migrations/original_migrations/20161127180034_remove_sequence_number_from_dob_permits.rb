class RemoveSequenceNumberFromDobPermits < ActiveRecord::Migration
  def change
    remove_column :dob_permits, :permit_sequence_num
  end
end
