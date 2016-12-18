class AddFieldsToDobPermit < ActiveRecord::Migration
  def change
    add_column :dob_permits, :job_start_date, :datetime
    add_column :dob_permits, :job_type, :string
    add_column :dob_permits, :job_num, :string
    add_column :dob_permits, :filling_status, :string
    add_column :dob_permits, :permit_type, :string
    add_column :dob_permits, :bldg_type, :string
  end
end
