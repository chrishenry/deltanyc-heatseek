# encoding: UTF-8
# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# Note that this schema.rb definition is the authoritative source for your
# database schema. If you need to create the application database on another
# system, you should be using db:schema:load, not running all the migrations
# from scratch. The latter is a flawed and unsustainable approach (the more migrations
# you'll amass, the slower it'll run and the greater likelihood for issues).
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema.define(version: 20161128023741) do

  create_table "TEST_violations", id: false, force: :cascade do |t|
    t.integer  "isn_dob_bis_viol",     limit: 4
    t.integer  "boro",                 limit: 4
    t.integer  "bin",                  limit: 4
    t.integer  "block",                limit: 4
    t.integer  "lot",                  limit: 4
    t.datetime "issue_date"
    t.string   "violation_type_code",  limit: 255
    t.integer  "violation_number",     limit: 4
    t.string   "house_number",         limit: 255
    t.string   "street",               limit: 255
    t.datetime "disposition_date"
    t.float    "disposition_comments", limit: 24
    t.float    "device_number",        limit: 24
    t.string   "description",          limit: 255
    t.string   "ecb_number",           limit: 255
    t.string   "number",               limit: 255
    t.string   "violation_category",   limit: 255
    t.string   "violation_type",       limit: 255
  end

  create_table "dob_permits", id: false, force: :cascade do |t|
    t.string   "borough",         limit: 255
    t.float    "bin_num",         limit: 24
    t.string   "house_num",       limit: 255
    t.string   "street_name",     limit: 255
    t.float    "job_num",         limit: 24
    t.float    "job_doc_num",     limit: 24
    t.string   "job_type",        limit: 255
    t.float    "block",           limit: 24
    t.string   "lot",             limit: 255
    t.string   "zip_code",        limit: 255
    t.float    "bldg_type",       limit: 24
    t.string   "residential",     limit: 255
    t.string   "work_type",       limit: 255
    t.string   "permit_status",   limit: 255
    t.string   "filing_status",   limit: 255
    t.string   "permit_type",     limit: 255
    t.datetime "filing_date"
    t.datetime "issuance_date"
    t.datetime "expiration_date"
    t.datetime "job_start_date"
    t.datetime "dobrundate"
  end

  create_table "dob_violations", id: false, force: :cascade do |t|
    t.integer  "isn_dob_bis_viol",     limit: 4
    t.string   "boro",                 limit: 255
    t.float    "bin",                  limit: 24
    t.string   "block",                limit: 255
    t.string   "lot",                  limit: 255
    t.datetime "issue_date"
    t.string   "violation_type_code",  limit: 255
    t.string   "violation_number",     limit: 255
    t.string   "house_number",         limit: 255
    t.string   "street",               limit: 255
    t.datetime "disposition_date"
    t.string   "disposition_comments", limit: 255
    t.string   "device_number",        limit: 255
    t.string   "description",          limit: 255
    t.string   "ecb_number",           limit: 255
    t.string   "number",               limit: 255
    t.string   "violation_category",   limit: 255
    t.string   "violation_type",       limit: 255
  end

  create_table "hdp_complaints", force: :cascade do |t|
    t.string   "type",              limit: 255
    t.integer  "major_category_id", limit: 4
    t.integer  "minor_category_id", limit: 4
    t.integer  "code_id",           limit: 4
    t.integer  "property_id",       limit: 4
    t.datetime "created_at",                    null: false
    t.datetime "updated_at",                    null: false
    t.string   "status",            limit: 255
    t.datetime "status_date"
    t.integer  "status_id",         limit: 4
  end

  create_table "hpd_buildings", id: false, force: :cascade do |t|
    t.integer "buildingid",         limit: 4
    t.integer "boroid",             limit: 4
    t.string  "boro",               limit: 255
    t.string  "housenumber",        limit: 255
    t.string  "lowhousenumber",     limit: 255
    t.string  "highhousenumber",    limit: 255
    t.string  "streetname",         limit: 255
    t.string  "zip",                limit: 255
    t.integer "block",              limit: 4
    t.integer "lot",                limit: 4
    t.float   "bin",                limit: 24
    t.integer "communityboard",     limit: 4
    t.float   "censustract",        limit: 24
    t.string  "managementprogram",  limit: 255
    t.float   "dobbuildingclassid", limit: 24
    t.string  "dobbuildingclass",   limit: 255
    t.float   "legalstories",       limit: 24
    t.float   "legalclassa",        limit: 24
    t.float   "legalclassb",        limit: 24
    t.integer "registrationid",     limit: 4
    t.string  "lifecycle",          limit: 255
    t.integer "recordstatusid",     limit: 4
    t.string  "recordstatus",       limit: 255
  end

  create_table "hpd_complaints", id: false, force: :cascade do |t|
    t.integer  "complaintid",    limit: 4
    t.integer  "buildingid",     limit: 4
    t.integer  "boroughid",      limit: 4
    t.string   "borough",        limit: 255
    t.string   "housenumber",    limit: 255
    t.string   "streetname",     limit: 255
    t.float    "zip",            limit: 24
    t.integer  "block",          limit: 4
    t.integer  "lot",            limit: 4
    t.string   "apartment",      limit: 255
    t.integer  "communityboard", limit: 4
    t.datetime "receiveddate"
    t.integer  "statusid",       limit: 4
    t.string   "status",         limit: 255
    t.datetime "statusdate"
  end

  create_table "hpd_complaintsProb", id: false, force: :cascade do |t|
    t.integer  "problemid",         limit: 4
    t.integer  "complaintid",       limit: 4
    t.integer  "unittypeid",        limit: 4
    t.string   "unittype",          limit: 255
    t.integer  "spacetypeid",       limit: 4
    t.string   "spacetype",         limit: 255
    t.integer  "typeid",            limit: 4
    t.string   "type",              limit: 255
    t.integer  "majorcategoryid",   limit: 4
    t.string   "majorcategory",     limit: 255
    t.integer  "minorcategoryid",   limit: 4
    t.string   "minorcategory",     limit: 255
    t.integer  "codeid",            limit: 4
    t.string   "code",              limit: 255
    t.integer  "statusid",          limit: 4
    t.string   "status",            limit: 255
    t.datetime "statusdate"
    t.string   "statusdescription", limit: 255
  end

  create_table "hpd_litigations", id: false, force: :cascade do |t|
    t.integer  "litigationid",  limit: 4
    t.integer  "buildingid",    limit: 4
    t.integer  "boroid",        limit: 4
    t.string   "boro",          limit: 255
    t.string   "housenumber",   limit: 255
    t.string   "streetname",    limit: 255
    t.float    "zip",           limit: 24
    t.integer  "block",         limit: 4
    t.integer  "lot",           limit: 4
    t.string   "casetype",      limit: 255
    t.datetime "caseopendate"
    t.string   "casestatus",    limit: 255
    t.string   "casejudgement", limit: 255
  end

  create_table "hpd_registrationContact", id: false, force: :cascade do |t|
    t.integer "registrationcontactid", limit: 4
    t.integer "registrationid",        limit: 4
    t.string  "type",                  limit: 255
    t.string  "contactdescription",    limit: 255
    t.string  "corporationname",       limit: 255
    t.string  "title",                 limit: 255
    t.string  "firstname",             limit: 255
    t.string  "middleinitial",         limit: 255
    t.string  "lastname",              limit: 255
    t.string  "businesshousenumber",   limit: 255
    t.string  "businessstreetname",    limit: 255
    t.string  "businessapartment",     limit: 255
    t.string  "businesscity",          limit: 255
    t.string  "businessstate",         limit: 255
    t.string  "businesszip",           limit: 255
  end

  create_table "hpd_registrations", id: false, force: :cascade do |t|
    t.integer  "registrationid",       limit: 4
    t.integer  "buildingid",           limit: 4
    t.integer  "boroid",               limit: 4
    t.string   "boro",                 limit: 255
    t.string   "housenumber",          limit: 255
    t.string   "lowhousenumber",       limit: 255
    t.string   "highhousenumber",      limit: 255
    t.string   "streetname",           limit: 255
    t.integer  "streetcode",           limit: 4
    t.float    "zip",                  limit: 24
    t.integer  "block",                limit: 4
    t.integer  "lot",                  limit: 4
    t.float    "bin",                  limit: 24
    t.integer  "communityboard",       limit: 4
    t.datetime "lastregistrationdate"
    t.datetime "registrationenddate"
  end

  create_table "hpd_violations", id: false, force: :cascade do |t|
    t.integer  "violationid",           limit: 4
    t.integer  "buildingid",            limit: 4
    t.integer  "registrationid",        limit: 4
    t.integer  "boroid",                limit: 4
    t.string   "boro",                  limit: 255
    t.string   "housenumber",           limit: 255
    t.string   "lowhousenumber",        limit: 255
    t.string   "highhousenumber",       limit: 255
    t.string   "streetname",            limit: 255
    t.integer  "streetcode",            limit: 4
    t.float    "zip",                   limit: 24
    t.string   "apartment",             limit: 255
    t.string   "story",                 limit: 255
    t.integer  "block",                 limit: 4
    t.integer  "lot",                   limit: 4
    t.string   "class",                 limit: 255
    t.datetime "inspectiondate"
    t.datetime "approveddate"
    t.datetime "originalcertifybydate"
    t.datetime "originalcorrectbydate"
    t.datetime "newcertifybydate"
    t.datetime "newcorrectbydate"
    t.datetime "certifieddate"
    t.string   "ordernumber",           limit: 255
    t.float    "novid",                 limit: 24
    t.string   "novdescription",        limit: 255
    t.datetime "novissueddate"
    t.integer  "currentstatusid",       limit: 4
    t.string   "currentstatus",         limit: 255
    t.datetime "currentstatusdate"
  end

  create_table "litigations", force: :cascade do |t|
    t.string   "case_type",      limit: 255
    t.boolean  "case_judgement"
    t.integer  "property_id",    limit: 4
    t.datetime "created_at",                 null: false
    t.datetime "updated_at",                 null: false
  end

  create_table "owners", force: :cascade do |t|
    t.string   "name",             limit: 255
    t.string   "address_line_one", limit: 255
    t.string   "address_line_two", limit: 255
    t.string   "city",             limit: 255
    t.string   "state",            limit: 255
    t.string   "zipcode",          limit: 255
    t.datetime "created_at",                   null: false
    t.datetime "updated_at",                   null: false
  end

  create_table "properties", force: :cascade do |t|
    t.string   "street_address",  limit: 255
    t.string   "city",            limit: 255
    t.string   "state",           limit: 255
    t.string   "zipcode",         limit: 255
    t.integer  "total_units",     limit: 4
    t.string   "bbl",             limit: 255
    t.string   "bin",             limit: 255
    t.boolean  "rent_stabilized"
    t.integer  "owner_id",        limit: 4
    t.datetime "created_at",                  null: false
    t.datetime "updated_at",                  null: false
  end

  create_table "complaint_311s", force: :cascade do |t|
    t.integer  "property_id",            limit: 4
    t.datetime "created_date"
    t.datetime "closed_date"
    t.string   "agency",                 limit: 255
    t.string   "complaint_type",         limit: 255
    t.string   "status",                 limit: 255
    t.datetime "due_date"
    t.string   "resolution_description", limit: 255
    t.datetime "created_at",                         null: false
    t.datetime "updated_at",                         null: false
  end

  create_table "dob_permits", force: :cascade do |t|
    t.integer  "property_id",     limit: 4
    t.string   "borough",         limit: 255
    t.float    "bin",             limit: 24
    t.float    "block",           limit: 24
    t.string   "lot",             limit: 255
    t.string   "permit_status",   limit: 255
    t.datetime "filing_date"
    t.datetime "expiration_date"
    t.datetime "created_at",                  null: false
    t.datetime "updated_at",                  null: false
    t.string   "work_type",       limit: 255
  end

  create_table "dob_violations", force: :cascade do |t|
    t.integer  "property_id",    limit: 4
    t.string   "violation_type", limit: 255
    t.datetime "created_at",                 null: false
    t.datetime "updated_at",                 null: false
  end

  create_table "hdp_complaints", force: :cascade do |t|
    t.string   "complaint_type",    limit: 255
    t.integer  "major_category_id", limit: 4
    t.integer  "minor_category_id", limit: 4
    t.integer  "code_id",           limit: 4
    t.integer  "property_id",       limit: 4
    t.datetime "created_at",                    null: false
    t.datetime "updated_at",                    null: false
    t.string   "status",            limit: 255
    t.datetime "status_date"
    t.integer  "status_id",         limit: 4
  end

  create_table "hdp_violations", force: :cascade do |t|
    t.integer  "property_id",         limit: 4
    t.string   "violation_class",     limit: 255
    t.datetime "inspection_date"
    t.datetime "certified_date"
    t.string   "order_number",        limit: 255
    t.float    "novid",               limit: 24
    t.string   "nov_description",     limit: 255
    t.string   "current_status",      limit: 255
    t.datetime "current_status_date"
    t.datetime "created_at",                      null: false
    t.datetime "updated_at",                      null: false
  end

  create_table "litigations", force: :cascade do |t|
    t.string   "case_type",      limit: 255
    t.boolean  "case_judgement"
    t.integer  "property_id",    limit: 4
    t.datetime "created_at",                 null: false
    t.datetime "updated_at",                 null: false
  end

  create_table "owner_properties", force: :cascade do |t|
    t.integer  "property_id", limit: 4
    t.integer  "owner_id",    limit: 4
    t.datetime "created_at",            null: false
    t.datetime "updated_at",            null: false
  end

  create_table "owners", force: :cascade do |t|
    t.string   "name",             limit: 255
    t.string   "address_line_one", limit: 255
    t.string   "address_line_two", limit: 255
    t.string   "city",             limit: 255
    t.string   "state",            limit: 255
    t.string   "zipcode",          limit: 255
    t.datetime "created_at",                   null: false
    t.datetime "updated_at",                   null: false
  end

  create_table "properties", force: :cascade do |t|
    t.string   "street_address",  limit: 255
    t.string   "city",            limit: 255
    t.string   "state",           limit: 255
    t.string   "zipcode",         limit: 255
    t.integer  "total_units",     limit: 4
    t.string   "bbl",             limit: 255
    t.string   "bin",             limit: 255
    t.boolean  "rent_stabilized"
    t.integer  "owner_id",        limit: 4
    t.datetime "created_at",                  null: false
    t.datetime "updated_at",                  null: false
  end

end
