namespace :db_connector do

  # Create a consistent boro value
  @boros = {
    'MN' => 'MANHATTAN',
    'BK' => 'BROOKLYN',
    'BX' => 'BRONX',
    'SI' => 'STATEN ISLAND',
    'QN' => 'QUEENS',
  }

  def get_short_boro(long_name)
    @boros.select{|key, value| value == long_name }
  end

  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    # Load addresses from Pluto
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,total_units,borough,block,lot,created_at,updated_at)
    SELECT TRIM(address), 'New York', 'New York', zipcode, unitstotal, borough, block, lot, NOW(), NOW() FROM pluto_nyc;"
    records_array = conn.execute(sql)

    @boros.each do |key, value|
      sql = "UPDATE hpd_buildings SET boro = '#{key}' WHERE boro = '#{value}';"
      # conn.execute(sql)
    end

    # Load addresses from HPD. This will catch additional addresses in hpd that are *not* in pluto
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,hpd_registration_id,borough,block,lot,created_at,updated_at)
    SELECT TRIM(streetname), 'New York', 'New York', zip, registrationid, boro, block, lot, NOW(), NOW() FROM hpd_buildings;"
    # conn.execute(sql)

    # Find properties without hpd_reg_id, and match the reg_id from hpd
    sql = "SELECT boro, block, lot, registrationid FROM hpd_buildings WHERE registrationid NOT IN (SELECT hpd_registration_id FROM r_properties WHERE hpd_registration_id IS NOT NULL)"
    reg_ids = conn.execute(sql)

    reg_ids.each do |reg_id|
      prop = Property.find_by(borough: reg_id[0], block: reg_id[1], lot: reg_id[2])

      prop.hpd_registration_id = reg_id[3]
      prop.save
    end

  end

  desc "Create owners"
  task owners: :environment do

    conn = ActiveRecord::Base.connection

    indexes = Hash[
      "hpd_registrations" => "registrationid",
      "hpd_registration_contact" => "registrationid"
    ]

    indexes.each do |table, index_|
      if not conn.index_exists?(table, index_) then
        conn.add_index(table, index_)
      end
    end


    # sql = "SELECT COUNT(*) AS cnt FROM hpd_registration_contact hrc INNER JOIN hpd_registrations hr ON hrc.registrationid = hr.registrationid;"
    # count_result = conn.exec_query(sql).to_hash[0]['cnt']

    # puts count_result

    # sql = "SELECT * FROM hpd_registration_contact hrc INNER JOIN hpd_registrations hr ON hrc.registrationid = hr.registrationid;"
    sql = "SELECT * FROM hpd_registration_contact hr WHERE
           businesshousenumber IS NOT NULL AND
           businessstreetname IS NOT NULL AND
            businessapartment IS NOT NULL AND
                 businesscity IS NOT NULL AND
                businessstate IS NOT NULL AND
                  businesszip IS NOT NULL;"
    owners_result = conn.exec_query(sql).to_hash


    owners_result.each do |owner|
      puts "*********************owner"

      # short_boro = @boros.key(owner['boro'])
      # prop = Property.find_by(borough: short_boro, block: owner['block'], lot: owner['lot'])
      # puts prop.id

      prop2 = Property.find_by(hpd_registration_id: owner['registrationid'])

      if prop2 then

        if Owner.find_by(hpd_registration_contact_id: owner['registrationcontactid']) then
          next
        end

        owner = Owner.new do |o|
          o.name = "#{owner['firstname']} #{owner['middleinitial']} #{owner['lastname']}".sub! '  ', ' '
          o.corporation_name = owner['corporationname']
          o.address_line_one = "#{owner['businesshousenumber']} #{owner['businessstreetname']}"
          o.address_line_two = owner['businessapartment']
          o.city = owner['businesscity']
          o.state = owner['businessstate']
          o.zipcode = owner['businesszip']
          o.hpd_registration_id = owner['registrationid']
          o.hpd_registration_contact_id = owner['registrationcontactid']
        end

        prop2.owners << owner

      end

    end

  end

end
