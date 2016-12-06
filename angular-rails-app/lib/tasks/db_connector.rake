namespace :db_connector do
  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    # Load addresses from Pluto
    # sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,total_units,borough,block,lot,created_at,updated_at)
    # SELECT TRIM(address), 'New York', 'New York', zipcode, unitstotal, borough, block, lot, NOW(), NOW() FROM pluto_nyc;"
    # records_array = ActiveRecord::Base.connection.execute(sql)

    # Create a consistent boro value
    boros = {
      'MN' => 'MANHATTAN',
      'BK' => 'BROOKLYN',
      'BX' => 'BRONX',
      'SI' => 'STATEN ISLAND',
      'QN' => 'QUEENS',
    }

    boros.each do |key, value|
      sql = "UPDATE hpd_buildings SET boro = '#{key}' WHERE boro = '#{value}';"
      # ActiveRecord::Base.connection.execute(sql)
    end

    # Load addresses from HPD. This will catch additional addresses in hpd that are *not* in pluto
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,hpd_registration_id,borough,block,lot,created_at,updated_at)
    SELECT TRIM(streetname), 'New York', 'New York', zip, registrationid, boro, block, lot, NOW(), NOW() FROM hpd_buildings;"
    # ActiveRecord::Base.connection.execute(sql)

    # Find properties without hpd_reg_id, and match the reg_id from hpd
    sql = "SELECT boro, block, lot, registrationid FROM hpd_buildings WHERE registrationid NOT IN (SELECT hpd_registration_id FROM r_properties WHERE hpd_registration_id IS NOT NULL)"
    reg_ids = ActiveRecord::Base.connection.execute(sql)

    reg_ids.each do |reg_id|
      prop = Property.find_by(borough: reg_id[0], block: reg_id[1], lot: reg_id[2])

      prop.hpd_registration_id = reg_id[3]
      prop.save
    end

  end

end
