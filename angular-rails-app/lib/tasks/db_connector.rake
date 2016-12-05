namespace :db_connector do
  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,total_units,borough,block,lot,created_at,updated_at)
    SELECT TRIM(address), 'New York', 'New York', zipcode, unitstotal, borough, block, lot, NOW(), NOW() FROM pluto_nyc;"
    records_array = ActiveRecord::Base.connection.execute(sql)

    puts records_array

  end

end
