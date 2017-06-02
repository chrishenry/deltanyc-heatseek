require 'json'

namespace :db_connector do

  # Create a consistent boro value
  @boros = {
    'MN' => 'MANHATTAN',
    'BK' => 'BROOKLYN',
    'BX' => 'BRONX',
    'SI' => 'STATEN ISLAND',
    'QN' => 'QUEENS',
  }

  @boros_int = {
    1 => 'MN',
    2 => 'BX',
    3 => 'BK',
    4 => 'QN',
    5 => 'SI',
  }

  def nyc_geocode(house_number, street, boro)

    app_key = ENV['NY_GEOCLIENT_APP_ID']
    app_secret = ENV['NY_GEOCLIENT_APP_KEY']

    url = "https://api.cityofnewyork.us/geoclient/v1/address.json?houseNumber=#{house_number}&street=#{street}&borough=#{boro}&app_id=#{app_key}&app_key=#{app_secret}"
    response = HTTParty.get(url)
    JSON.parse(response.body)

  end

  def add_indexes(indexes)

    conn = ActiveRecord::Base.connection

    indexes.each do |ar|
      table = ar[0]
      col = ar[1]
      if not conn.index_exists?(table, col) then
        conn.add_index(table, col)
      end
    end

  end

  desc 'Run All'
  task :all do

    Rake::Task['db_connector:properties'].invoke()
    Rake::Task['db_connector:owners'].invoke()
    Rake::Task['db_connector:dob_permits'].invoke()
    Rake::Task['db_connector:dob_violations'].invoke()
    Rake::Task['db_connector:hpd_complaints'].invoke()
    Rake::Task['db_connector:hpd_litigations'].invoke()
    Rake::Task['db_connector:three11'].invoke()

  end

  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    conn = ActiveRecord::Base.connection

    # Load addresses from HPD.
    print "Copying from hpd_buildings..."
    sql = "INSERT IGNORE INTO properties "\
        "(street_address,city,state,zipcode,hpd_registration_id,borough,block,lot,bbl,created_at,updated_at) "\
        "SELECT CONCAT(TRIM(housenumber), ' ', TRIM(streetname)), boro, 'New York', zip, registrationid, boro, block, lot, bbl, NOW(),NOW() "\
        "FROM #{ENV['MYSQL_DATABASE_DATA']}.hpd_buildings WHERE streetname != '' AND streetname IS NOT NULL AND registrationid != 0;"
    conn.execute(sql)

    # Add unit counts to HPD data.
    sql = "UPDATE properties "\
        "INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.pluto_nyc ON properties.bbl = #{ENV['MYSQL_DATABASE_DATA']}.pluto_nyc.bbl AND properties.total_units IS NULL "\
        "SET properties.total_units = #{ENV['MYSQL_DATABASE_DATA']}.pluto_nyc.unitstotal;"
    conn.execute(sql)
    puts "done"

    # Load addresses from Pluto. This will add address that aren't in HPD.
    print "Copying from pluto_nyc..."
    sql = "INSERT IGNORE INTO properties "\
        "(street_address,city,state,zipcode,total_units,borough,block,lot,bbl,created_at,updated_at) "\
        "SELECT TRIM(address), borough, 'New York', zipcode, unitstotal, borough, block, lot, bbl, NOW(), NOW() "\
        "FROM #{ENV['MYSQL_DATABASE_DATA']}.pluto_nyc WHERE address != '';"
    conn.execute(sql)
    puts "done."

    print "Expanding city from 2 letter boro code..."
    @boros.each do |key, value|
      sql = "UPDATE properties SET city = '#{value.titleize}' WHERE city = '#{key}';"
      puts sql
      conn.execute(sql)
    end
    puts "done."

    # Find buildings imported from pluto_nyc that have hpd registration ids and add ids.
    sql = "SELECT bbl, registrationid FROM #{ENV['MYSQL_DATABASE_DATA']}.hpd_buildings "\
        "WHERE registrationid != 0 AND registrationid NOT IN "\
        "(SELECT hpd_registration_id FROM properties WHERE hpd_registration_id IS NOT NULL);"
    reg_ids = conn.execute(sql)
    reg_ids_count = reg_ids.count

    puts "Found #{reg_ids_count} addresses without registrationid...fixing."

    reg_ids.each_with_index do |reg_id, idx|
      prop = Property.find_by(bbl: reg_id[0])

      if prop.nil?
        next
      end

      prop.hpd_registration_id = reg_id[1]
      prop.save

      if idx % 100 == 0
        print "Saved #{idx}/#{reg_ids_count} \r"
        $stdout.flush
      end
    end

    # Pull in rent stabilized counts from rent_stab.
    print "Pulling in rent stabilized counts..."
    sql = "UPDATE properties "\
        "INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.rent_stabilization ON properties.bbl = #{ENV['MYSQL_DATABASE_DATA']}.rent_stabilization.ucbbl "\
        "SET properties.rent_stabilized = #{ENV['MYSQL_DATABASE_DATA']}.rent_stabilization.2015uc;"
    conn.execute(sql)
    puts "done."

    puts "Finished importing properties"

  end

  desc "Create owners"
  task owners: :environment do

    conn = ActiveRecord::Base.connection

    sql_owners = "INSERT IGNORE INTO owners
        (name, corporation_name, address_line_one, address_line_two, city, state, zipcode, hpd_registration_id, hpd_registration_contact_id, hpd_type, created_at, updated_at)
        SELECT CONCAT_WS(' ', TRIM(firstname), TRIM(middleinitial), TRIM(lastname)), corporationname, CONCAT(TRIM(businesshousenumber), ' ', TRIM(businessstreetname)),
            businessapartment, businesscity, businessstate, businesszip, registrationid, registrationcontactid, type, NOW(), NOW()
        FROM #{ENV['MYSQL_DATABASE_DATA']}.hpd_registration_contacts;"
    sql_owner_properties = "INSERT IGNORE INTO owner_properties
          (property_id, owner_id, created_at, updated_at)
          SELECT properties.id, owners.id, NOW(), NOW()
          FROM owners INNER JOIN properties ON owners.hpd_registration_id = properties.hpd_registration_id;"

    conn.execute(sql_owners)
    conn.execute(sql_owner_properties)
  end

  desc "Pull in hpd complaints"
  task hpd_complaints: :environment do
    indexes = [
      ["#{ENV['MYSQL_DATABASE_DATA']}.hpd_complaints", "complaintid"],
      ["#{ENV['MYSQL_DATABASE_DATA']}.hpd_complaints_problems", "complaintid"],
    ]
    add_indexes(indexes)
    conn = ActiveRecord::Base.connection
    conn.execute 'TRUNCATE hpd_complaints;'
    # ATTENTION: For demo purposes, we are only pulling limited addresses based on the hpd reg id. See the WHERE condition
    sql = "INSERT IGNORE INTO hpd_complaints
        (property_id, received_date, complaint_id, apartment, status, status_date, status_id,
        complaint_type, major_category_id, major_category, minor_category_id, minor_category,
        code_id, code, description)
        SELECT p.id, c.receiveddate, c.complaintid, c.apartment, c.status,
        c.statusdate, c.statusid, prob.typeid, prob.majorcategory, prob.majorcategoryid, prob.minorcategory,
        prob.minorcategoryid, prob.code, prob.codeid, prob.statusdescription
        FROM properties AS p INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.hpd_complaints AS c
            ON p.bbl = c.bbl
        INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.hpd_complaints_problems AS prob
            ON c.complaintid = prob.complaintid;"
    conn.execute(sql)
  end

  desc "Pull in hpd litigations"
  task hpd_litigations: :environment do
    conn = ActiveRecord::Base.connection
    sql = "INSERT IGNORE INTO litigations
        (property_id, case_type, case_judgement, litigation_id, case_open_date,
        case_status)
        SELECT p.id, l.casetype, l.casejudgement, l.litigationid, l.caseopendate,
        l.casestatus
        FROM properties AS p INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.hpd_litigations AS l
            ON p.bbl = l.bbl;"
    conn.execute(sql)
  end

  desc "Pull in dob permits"
  task dob_permits: :environment do

    conn = ActiveRecord::Base.connection

    # This table doesn't have any sort of unique identifier,
    #   so there really isn't any way to ensure uniqueness,
    #   except for nuking the whole table every import.
    puts "Truncating #{DobPermit.table_name}"

    sql = "TRUNCATE #{DobPermit.table_name}"
    conn.execute(sql)

    puts "Inserting into #{DobPermit.table_name}"

    insert_sql = "INSERT IGNORE INTO dob_permits
        (property_id, permit_status, filing_date, expiration_date, work_type, job_start_date,
            job_type, job_num, filing_status, permit_type, bldg_type, created_at, updated_at)
        SELECT p.id, d.permit_status, d.filing_date, d.expiration_date, d.work_type,
            d.job_start_date, d.job_type, d.job_num, d.filing_status, d.permit_type,
            d.bldg_type, NOW(), NOW()
        FROM properties AS p INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.dob_permits AS d ON p.bbl = d.bbl;"
    conn.execute(insert_sql)

    puts "Done"

  end

  desc "Pull in dob violations"
  task dob_violations: :environment do

    conn = ActiveRecord::Base.connection

    puts "Adding indexes..."
    indexes = [
      ["#{ENV['MYSQL_DATABASE_DATA']}.dob_violations", "violation_type_code"]
    ]
    add_indexes(indexes)

    v_types = [
      "IMD", # -IMMEDIATE EMERGENCY",
      "COMPBLD", # -STRUCTURALLY COMPROMISED BUILDING",
      "HBLVIO", # -HIGH PRESSURE BOILER",
      "LL1080", # -LOCAL LAW 10/80 - FACADE",
      "P", # -PLUMBING",
      "EGNCY", # -EMERGENCY",
      "UB", # -UNSAFE BUILDINGS",
      "IMEGNCY", # -IMMEDIATE EMERGENCY",
      "LBLVIO", # -LOW PRESSURE BOILER",
      "LL1081", # -LOCAL LAW 10/81 - ELEVATOR",
      "LL6291", # -LOCAL LAW 62/91 - BOILERS",
      "C", # -CONSTRUCTION",
      "B", # -BOILER",
    ]

    in_list =  "\"" + v_types.join("\", \"") + "\""

    puts "Pulling dob violations..."
    sql = "INSERT IGNORE INTO dob_violations
        (property_id, isn_dob_bis_viol, violation_type_code, violation_type,
        violation_category, issue_date, disposition_date, disposition_comments)
        SELECT p.id, v.isn_dob_bis_viol, v.violation_type_code, v.violation_type,
        v.violation_category, v.issue_date, v.disposition_date,
        v.disposition_comments
        FROM properties AS p INNER JOIN #{ENV['MYSQL_DATABASE_DATA']}.dob_violations AS v
            ON p.bbl = v.bbl
        WHERE v.violation_type_code IN (#{in_list});"
    conn.execute(sql)

    puts "done"
  end

  desc "Pull in 311 complaints"
  task three11: :environment do

    conn = ActiveRecord::Base.connection

    indexes = [
      ["#{ENV['MYSQL_DATABASE_DATA']}.call_311", "borough"],
      ["#{ENV['MYSQL_DATABASE_DATA']}.call_311", "complaint_type"],
    ]

    puts "adding indexes"
    add_indexes(indexes)

    Complaint311::Categories.each do |category|

      sql = "SELECT * FROM #{ENV['MYSQL_DATABASE_DATA']}.call_311 WHERE incident_address IS NOT NULL AND borough != 'unspecified' AND incident_address != '' AND complaint_type = \"" + category + "\";"
      three11_results = conn.exec_query(sql).to_hash

      three11_results.each do |result|

        puts "******* #{category} *******"

        # Decently working regex to get ONLY street_number
        street_number = result['incident_address'].scan(/^[^\s]+/).join('')
        street = result['street_name']
        boro_id = result['borough']

        begin
          geo_data = nyc_geocode(street_number, street, boro_id)
        rescue Exception => _
          puts "GEO API error, pausing && continuing"
          sleep(1)
          next
        end

        boro = result['borough']
        block = geo_data['address']['bblTaxBlock'].to_i
        lot = geo_data['address']['bblTaxLot'].to_i

        prop = Property.find_by(borough: boro, block: block, lot: lot)

        if prop and not Complaint311.find_by(unique_key: result['unique_key'])

          puts "Found property, adding complaint"

          complaint = Complaint311.new do |c|
            c.property_id = prop.id
            c.unique_key = result['unique_key']
            c.created_date = result['created_date']
            c.closed_date = result['closed_date']
            c.agency = result['agency']
            c.complaint_type = result['complaint_type']
            c.status = result['status']
            c.due_date = result['due_date']
            c.resolution_description = result['resolution_description']
          end

          complaint.save

        end

      end

    end

  end

end

