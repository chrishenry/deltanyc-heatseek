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

    app_key = ENV['NY_GEOCLIENT_APP_KEY']
    app_secret = ENV['NY_GEOCLIENT_APP_SECRET']

    url = "https://api.cityofnewyork.us/geoclient/v1/address.json?houseNumber=#{house_number}&street=#{street}&borough=#{boro}&app_id=#{app_key}&app_key=#{app_secret}"
    response = HTTParty.get(url)
    JSON.parse(response.body)
  end

  def add_indexes(indexes)

    conn = ActiveRecord::Base.connection

    indexes.each do |table, index_|
      if not conn.index_exists?(table, index_) then
        conn.add_index(table, index_)
      end
    end

  end

  desc "Pull in properties from pluto and hpd_buildings"
  task properties: :environment do

    conn = ActiveRecord::Base.connection

    # Load addresses from Pluto
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,total_units,borough,block,lot,created_at,updated_at)
    SELECT TRIM(address), 'New York', 'New York', zipcode, unitstotal, borough, block, lot, NOW(), NOW() FROM pluto_nyc;"
    records_array = conn.execute(sql)

    @boros.each do |key, value|
      sql = "UPDATE hpd_buildings SET boro = '#{key}' WHERE boro = '#{value}';"
      conn.execute(sql)
    end

    # Load addresses from HPD. This will catch additional addresses in hpd that are *not* in pluto
    sql = "INSERT IGNORE INTO r_properties (street_address,city,state,zipcode,hpd_registration_id,borough,block,lot,created_at,updated_at)
    SELECT TRIM(streetname), 'New York', 'New York', zip, registrationid, boro, block, lot, NOW(), NOW() FROM hpd_buildings;"
    conn.execute(sql)

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
      "hpd_registration_contacts" => "registrationid"
    ]

    add_indexes(indexes)

    # sql = "SELECT COUNT(*) AS cnt FROM hpd_registration_contact hrc INNER JOIN hpd_registrations hr ON hrc.registrationid = hr.registrationid;"
    # count_result = conn.exec_query(sql).to_hash[0]['cnt']

    # puts count_result

    # sql = "SELECT * FROM hpd_registration_contact hrc INNER JOIN hpd_registrations hr ON hrc.registrationid = hr.registrationid;"
    sql = "SELECT * FROM hpd_registration_contacts hr WHERE
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

      boro = @boros_int[complaint['boroughid']]
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

      boro = @boros_int[litigation['boroid']]
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

    permits.each do |permit|

      boro = @boros.key(permit['borough'])
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
      puts "Saved permit"

    end

  end

  desc "Pull in dob violations"
  task dob_violations: :environment do

    conn = ActiveRecord::Base.connection

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

    sql = "SELECT * FROM dob_violations WHERE violation_type IN (#{in_list})"
    violation_results = conn.exec_query(sql).to_hash

    violation_results.each do |violation|

      if not DobViolation.find_by(isn_dob_bis_viol: violation['isn_dob_bis_viol']).nil?
        puts "Exists, skipping"
        next
      end

      boro = @boros_int[violation['boro'].to_i]
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

      puts "Saved violation"
      violation.save

    end



  end

  desc "Pull in 311 complaints"
  task three11: :environment do

    conn = ActiveRecord::Base.connection

    indexes = Hash[
      "call_311" => "complaint_type",
    ]

    add_indexes(indexes)

    # There are ~240 categories. We def don't care about all of them
    # This is just a guess as to what we *do* care about.
    three11_categories = [
      "Maintenance or Facility",
      "HEATING",
      "Building/Use",
      "APPLIANCE",
      "BEST/Site Safety",
      "Indoor Air Quality",
      "Air Quality",
      "Weatherization",
      "Water Quality",
      "Indoor Sewage",
      "Boilers",
      "Mold",
      "UNSANITARY CONDITION",
      "WATER LEAK",
      "HEAT/HOT WATER",
      "Standing Water",
      "Rodent",
      "Indoor Sewage",
      "Emergency Response Team (ERT)",
      "Lead",
      "Eviction",
    ]

    in_list =  "\"" + three11_categories.join("\", \"") + "\""

    sql = "SELECT * FROM call_311 WHERE incident_address IS NOT NULL AND borough != 'unspecified' AND complaint_type IN (" + in_list + ");"
    three11_results = conn.exec_query(sql).to_hash

    three11_results.each do |result|

      puts "**************"

      # Decently working regex to get ONLY street_number
      street_number = result['incident_address'].scan(/^[^\s]+/).join('')
      street = result['street_name']
      boro_id = @boros_int.key(@boros.key(result['borough']))

      puts result['borough']
      puts boro_id

      geo_data = nyc_geocode(street_number, street, boro_id)

      boro = @boros_int[geo_data['address']['bblBoroughCode'].to_i]
      block = geo_data['address']['bblTaxBlock'].to_i
      lot = geo_data['address']['bblTaxLot'].to_i

      prop = Property.find_by(borough: boro, block: block, lot: lot)

      if prop and not Complaint311.find_by(unique_key: result['unique_key'])

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

