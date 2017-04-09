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

  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    conn = ActiveRecord::Base.connection

    # Load addresses from HPD.
    print "Copying from hpd_buildings..."
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,hpd_registration_id,borough,block,lot,created_at,updated_at)
    SELECT CONCAT(TRIM(housenumber), ' ', TRIM(streetname)), boro, 'New York', zip, registrationid, boro, block, lot, NOW(), NOW() FROM hpd_buildings WHERE streetname != '' AND streetname IS NOT NULL AND registrationid != 0;"
    conn.execute(sql)
    puts "done"

    # Load addresses from Pluto. This will add address that aren't in HPD.
    print "Copying from pluto_nyc..."
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,total_units,borough,block,lot,created_at,updated_at)
    SELECT TRIM(address), borough, 'New York', zipcode, unitstotal, borough, block, lot, NOW(), NOW() FROM pluto_nyc WHERE address != '';"
    records_array = conn.execute(sql)
    puts "done."

    print "Expanding city from 2 letter boro code..."
    @boros.each do |key, value|
      sql = "UPDATE r_properties SET city = '#{value.titleize}' WHERE city = '#{key}';"
      puts sql
      conn.execute(sql)
    end
    puts "done."

    # Find hpd_buildings that are hpd_reg_id, and match the reg_id from hpd
    sql = "SELECT boro, block, lot, registrationid FROM hpd_buildings WHERE registrationid != 0 AND registrationid NOT IN (SELECT hpd_registration_id FROM r_properties WHERE hpd_registration_id IS NOT NULL)"
    reg_ids = conn.execute(sql)
    reg_ids_count = reg_ids.count

    puts "Found #{reg_ids_count} addresses without registrationid...fixing."

    reg_ids.each_with_index do |reg_id, idx|
      prop = Property.find_by(borough: reg_id[0], block: reg_id[1], lot: reg_id[2])

      prop.hpd_registration_id = reg_id[3]
      prop.save

      print "Saved #{idx}/#{reg_ids_count} \r"
      $stdout.flush
    end

    puts "Finished importing properties"

  end

  desc "Create owners"
  task owners: :environment do

    conn = ActiveRecord::Base.connection

    indexes = [
      ["hpd_registrations", "registrationid"],
      ["hpd_registration_contacts", "registrationid"]
    ]

    add_indexes(indexes)

    sql = "SELECT * FROM hpd_registration_contacts hr WHERE
           firstname IS NOT NULL AND
           firstname != '' AND
           lastname IS NOT NULL AND
           lastname != '' AND
           corporationname IS NOT NULL AND
           corporationname != '' AND
           businesshousenumber IS NOT NULL AND
           businessstreetname IS NOT NULL AND
                 businesscity IS NOT NULL AND
                businessstate IS NOT NULL AND
                  businesszip IS NOT NULL;"
    owners_result = conn.exec_query(sql).to_hash

    owners_result_count = owners_result.count

    puts "Found #{owners_result_count} owners...matching."

    owners_result.each_with_index do |owner, idx|

      print "Saving #{idx}/#{owners_result_count} \r"
      $stdout.flush

      prop = Property.find_by(hpd_registration_id: owner['registrationid'])

      if prop then

        if Owner.find_by(hpd_registration_contact_id: owner['registrationcontactid']) then
          next
        end

        begin

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

          prop.owners << owner
          prop.save

        rescue Exception => e
          puts e.message
        end

      end

      print "Done."

    end

  end

  desc "Pull in hpd complaints"
  task hpd_complaints: :environment do

    conn = ActiveRecord::Base.connection

    sql = "SELECT * FROM hpd_complaints"
    complaints = conn.exec_query(sql).to_hash

    puts "Found #{complaints.length} complaints"

    complaints.each do |complaint|

      if not HpdComplaint.find_by(complaint_id: complaint['complaintid']).nil?
        puts "Exists, skipping"
        next
      end

      boro = complaint['boroughid']
      block = complaint['block']
      lot = complaint['lot']

      prop = Property.find_by(borough: boro, block: block, lot: lot)

      if prop.nil?
        next
      end

      hpd_complaint = HpdComplaint.new do |hc|
        #   hc.complaint_type =
        #   hc.major_category_id =
        #   hc.minor_category_id =
        #   hc.code_id =
        hc.property_id = prop.id
        hc.received_date = complaint['receiveddate']
        hc.complaint_id = complaint['complaintid']
        hc.apartment = complaint['apartment']
        hc.status = complaint['status']
        hc.status_date = complaint['statusdate']
        hc.status_id = complaint['statusid']
      end

      hpd_complaint.save
      puts "Saved complaint"

    end

  end

  desc "Pull in hpd litigations"
  task hpd_litigations: :environment do

    conn = ActiveRecord::Base.connection

    sql = "SELECT * FROM hpd_litigations"
    litigations = conn.exec_query(sql).to_hash

    puts "Found #{litigations.length} cases"

    litigations.each do |litigation|

      if not Litigation.find_by(litigation_id: litigation['litigationid']).nil?
        puts "Exists, skipping"
        next
      end

      boro = litigation['boroid']
      block = litigation['block']
      lot = litigation['lot']

      prop = Property.find_by(borough: boro, block: block, lot: lot)

      if prop.nil?
        next
      end

      lit = Litigation.new do |l|
        l.property_id = prop.id
        l.case_type = litigation['casetype']
        l.case_judgement = litigation['casejudgement']
        l.litigation_id = litigation['litigationid']
        l.case_open_date = litigation['caseopendate']
        l.case_status = litigation['casestatus']
      end

      lit.save
      puts "Saved case"

    end

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

    sql = "SELECT * FROM dob_permits"
    permits = conn.exec_query(sql).to_hash

    puts "Found #{permits.length} permits"

    permits.each_with_index do |permit, idx|

      print "Saving #{idx}/#{permits.length} \r"
      $stdout.flush

      boro = permit['borough']
      block = permit['block'].to_i
      lot = permit['lot'].to_i

      prop = Property.find_by(borough: boro, block: block, lot: lot)

      if prop.nil?
        next
      end

      permit = DobPermit.new do |d|
        d.property_id = prop.id
        d.permit_status = permit['permit_status']
        d.filing_date = permit['filling_date']
        d.expiration_date = permit['expiration_date']
        d.work_type = permit['work_type']
        d.job_start_date = permit['job_start_date']
        d.job_type = permit['job_type']
        d.job_num = permit['job_num']
        d.job_type = permit['job_type']
        d.filling_status = permit['filling_status']
        d.permit_status = permit['permit_status']
        d.permit_type = permit['permit_type']
        d.bldg_type = permit['bldg_type']
      end

      permit.save

    end

  end

  desc "Pull in dob violations"
  task dob_violations: :environment do

    conn = ActiveRecord::Base.connection

    puts "Adding indexes..."
    indexes = [
      ["dob_violations", "violation_type"]
    ]
    add_indexes(indexes)

    v_types = [
      "IMD-IMMEDIATE EMERGENCY",
      "COMPBLD-STRUCTURALLY COMPROMISED BUILDING",
      "HBLVIO-HIGH PRESSURE BOILER",
      "LL1080-LOCAL LAW 10/80 - FACADE",
      "P-PLUMBING",
      "EGNCY-EMERGENCY",
      "UB-UNSAFE BUILDINGS",
      "IMEGNCY-IMMEDIATE EMERGENCY",
      "LBLVIO-LOW PRESSURE BOILER",
      "LL1081-LOCAL LAW 10/81 - ELEVATOR",
      "LL6291-LOCAL LAW 62/91 - BOILERS",
      "C-CONSTRUCTION",
      "B-BOILER",
    ]

    in_list =  "\"" + v_types.join("\", \"") + "\""

    puts "Pulling dob violations..."
    sql = "SELECT * FROM dob_violations WHERE violation_type IN (#{in_list})"
    violation_results = conn.exec_query(sql).to_hash

    violation_results.each_with_index do |violation,idx|

      print "Saving #{idx}/#{violation_results.length} \r"
      $stdout.flush

      if not DobViolation.find_by(isn_dob_bis_viol: violation['isn_dob_bis_viol']).nil?
        puts "Exists, skipping"
        next
      end

      boro = violation['boro']
      block = violation['block'].to_i
      lot = violation['lot'].to_i

      prop = Property.find_by(borough: boro, block: block, lot: lot)

      if prop.nil?
        next
      end

      violation = DobViolation.new do |d|
        d.property_id = prop.id
        d.isn_dob_bis_viol = violation['isn_dob_bis_viol']
        d.violation_type = violation['violation_type']
        d.violation_category = violation['violation_category']
        d.issue_date = violation['issue_date']
        d.disposition_date = violation['disposition_date']
        d.disposition_comments = violation['disposition_comments']
      end

      violation.save

    end

  end

  desc "Pull in 311 complaints"
  task three11: :environment do

    conn = ActiveRecord::Base.connection

    indexes = [
      ["call_311", "borough"],
      ["call_311", "complaint_type"],
    ]

    puts "adding indexes"
    add_indexes(indexes)

    Complaint311::Categories.each do |category|

      sql = "SELECT * FROM call_311 WHERE incident_address IS NOT NULL AND borough != 'unspecified' AND incident_address != '' AND complaint_type = \"" + category + "\";"
      three11_results = conn.exec_query(sql).to_hash

      three11_results.each do |result|

        puts "******* #{category} *******"

        # Decently working regex to get ONLY street_number
        street_number = result['incident_address'].scan(/^[^\s]+/).join('')
        street = result['street_name']
        boro_id = result['borough']

        begin
          geo_data = nyc_geocode(street_number, street, boro_id)
        rescue Exception => e
          puts "GEO API error, pausing && continuing"
          sleep(1)
          next
        end

        boro = @boros_int[geo_data['address']['bblBoroughCode'].to_i]
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

