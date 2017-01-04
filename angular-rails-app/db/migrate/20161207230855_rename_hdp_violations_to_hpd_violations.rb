class RenameHdpViolationsToHpdViolations < ActiveRecord::Migration
  def change
    rename_table :hdp_violations, :hpd_violations
  end
end
