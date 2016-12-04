class RemoveCommunityBoardFromDobPermits < ActiveRecord::Migration
  def change
    remove_column :dob_permits, :community_board
  end
end
