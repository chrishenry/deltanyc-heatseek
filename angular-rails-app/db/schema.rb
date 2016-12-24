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

ActiveRecord::Schema.define(version: 20161219171930) do

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

  create_table "call_311", force: :cascade do |t|
    t.integer  "unique_key",                     limit: 8
    t.datetime "created_date"
    t.datetime "closed_date"
    t.string   "agency",                         limit: 255
    t.string   "complaint_type",                 limit: 255
    t.string   "descriptor",                     limit: 255
    t.string   "incident_zip",                   limit: 255
    t.string   "incident_address",               limit: 255
    t.string   "street_name",                    limit: 255
    t.string   "cross_street_1",                 limit: 255
    t.string   "cross_street_2",                 limit: 255
    t.string   "intersection_street_1",          limit: 255
    t.string   "intersection_street_2",          limit: 255
    t.string   "city",                           limit: 255
    t.string   "status",                         limit: 255
    t.datetime "due_date"
    t.string   "resolution_description",         limit: 255
    t.datetime "resolution_action_updated_date"
    t.string   "borough",                        limit: 255
    t.float    "latitude",                       limit: 24
    t.float    "longitude",                      limit: 24
    t.string   "location",                       limit: 255
  end

  add_index "call_311", ["complaint_type"], name: "index_call_311_on_complaint_type", using: :btree

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

  create_table "hpd_buildings", force: :cascade do |t|
    t.integer "buildingid",         limit: 8
    t.integer "boroid",             limit: 8
    t.string  "boro",               limit: 255
    t.string  "housenumber",        limit: 255
    t.string  "lowhousenumber",     limit: 255
    t.string  "highhousenumber",    limit: 255
    t.string  "streetname",         limit: 255
    t.string  "zip",                limit: 255
    t.integer "block",              limit: 8
    t.integer "lot",                limit: 8
    t.float   "bin",                limit: 24
    t.integer "communityboard",     limit: 8
    t.float   "censustract",        limit: 24
    t.string  "managementprogram",  limit: 255
    t.float   "dobbuildingclassid", limit: 24
    t.string  "dobbuildingclass",   limit: 255
    t.float   "legalstories",       limit: 24
    t.float   "legalclassa",        limit: 24
    t.float   "legalclassb",        limit: 24
    t.integer "registrationid",     limit: 8
    t.string  "lifecycle",          limit: 255
    t.integer "recordstatusid",     limit: 8
    t.string  "recordstatus",       limit: 255
  end

  create_table "hpd_complaints", id: false, force: :cascade do |t|
    t.integer  "complaintid",    limit: 8
    t.integer  "buildingid",     limit: 8
    t.integer  "boroughid",      limit: 8
    t.string   "borough",        limit: 255
    t.string   "housenumber",    limit: 255
    t.string   "streetname",     limit: 255
    t.float    "zip",            limit: 24
    t.integer  "block",          limit: 8
    t.integer  "lot",            limit: 8
    t.string   "apartment",      limit: 255
    t.integer  "communityboard", limit: 8
    t.datetime "receiveddate"
    t.integer  "statusid",       limit: 8
    t.string   "status",         limit: 255
    t.datetime "statusdate"
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

  create_table "hpd_registration_contact", force: :cascade do |t|
    t.integer "registrationcontactid", limit: 8
    t.integer "registrationid",        limit: 8
    t.string  "type",                  limit: 255
    t.string  "corporationname",       limit: 255
    t.string  "contactdescription",    limit: 255
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

  add_index "hpd_registration_contact", ["registrationid"], name: "index_hpd_registration_contact_on_registrationid", using: :btree

  create_table "hpd_registrations", force: :cascade do |t|
    t.integer  "registrationid",       limit: 8
    t.integer  "buildingid",           limit: 8
    t.integer  "boroid",               limit: 8
    t.string   "boro",                 limit: 255
    t.string   "housenumber",          limit: 255
    t.string   "lowhousenumber",       limit: 255
    t.string   "highhousenumber",      limit: 255
    t.string   "streetname",           limit: 255
    t.integer  "streetcode",           limit: 8
    t.float    "zip",                  limit: 24
    t.integer  "block",                limit: 8
    t.integer  "lot",                  limit: 8
    t.float    "bin",                  limit: 24
    t.integer  "communityboard",       limit: 8
    t.datetime "lastregistrationdate"
    t.datetime "registrationenddate"
  end

  add_index "hpd_registrations", ["registrationid"], name: "index_hpd_registrations_on_registrationid", using: :btree

  create_table "pluto_nyc", force: :cascade do |t|
    t.string   "borough",       limit: 255
    t.integer  "block",         limit: 8
    t.integer  "lot",           limit: 8
    t.integer  "cd",            limit: 8
    t.float    "ct2010",        limit: 24
    t.float    "cb2010",        limit: 24
    t.float    "schooldist",    limit: 24
    t.float    "council",       limit: 24
    t.float    "zipcode",       limit: 24
    t.string   "firecomp",      limit: 255
    t.float    "policeprct",    limit: 24
    t.float    "healtharea",    limit: 24
    t.float    "sanitboro",     limit: 24
    t.float    "sanitdistrict", limit: 24
    t.string   "sanitsub",      limit: 255
    t.string   "address",       limit: 255
    t.string   "zonedist1",     limit: 255
    t.string   "zonedist2",     limit: 255
    t.string   "zonedist3",     limit: 255
    t.string   "zonedist4",     limit: 255
    t.string   "overlay1",      limit: 255
    t.string   "overlay2",      limit: 255
    t.string   "spdist1",       limit: 255
    t.string   "spdist2",       limit: 255
    t.string   "spdist3",       limit: 255
    t.string   "ltdheight",     limit: 255
    t.string   "splitzone",     limit: 255
    t.string   "bldgclass",     limit: 255
    t.float    "landuse",       limit: 24
    t.integer  "easements",     limit: 8
    t.string   "ownertype",     limit: 255
    t.string   "ownername",     limit: 255
    t.integer  "lotarea",       limit: 8
    t.integer  "bldgarea",      limit: 8
    t.integer  "comarea",       limit: 8
    t.integer  "resarea",       limit: 8
    t.integer  "officearea",    limit: 8
    t.integer  "retailarea",    limit: 8
    t.integer  "garagearea",    limit: 8
    t.integer  "strgearea",     limit: 8
    t.integer  "factryarea",    limit: 8
    t.integer  "otherarea",     limit: 8
    t.integer  "areasource",    limit: 8
    t.integer  "numbldgs",      limit: 8
    t.float    "numfloors",     limit: 24
    t.integer  "unitsres",      limit: 8
    t.integer  "unitstotal",    limit: 8
    t.float    "lotfront",      limit: 24
    t.float    "lotdepth",      limit: 24
    t.float    "bldgfront",     limit: 24
    t.float    "bldgdepth",     limit: 24
    t.string   "ext",           limit: 255
    t.float    "proxcode",      limit: 24
    t.string   "irrlotcode",    limit: 255
    t.float    "lottype",       limit: 24
    t.float    "bsmtcode",      limit: 24
    t.integer  "assessland",    limit: 8
    t.integer  "assesstot",     limit: 8
    t.integer  "exemptland",    limit: 8
    t.integer  "exempttot",     limit: 8
    t.integer  "yearbuilt",     limit: 8
    t.integer  "yearalter1",    limit: 8
    t.integer  "yearalter2",    limit: 8
    t.string   "histdist",      limit: 255
    t.string   "landmark",      limit: 255
    t.float    "builtfar",      limit: 24
    t.float    "residfar",      limit: 24
    t.float    "commfar",       limit: 24
    t.float    "facilfar",      limit: 24
    t.integer  "borocode",      limit: 8
    t.integer  "bbl",           limit: 8
    t.integer  "condono",       limit: 8
    t.integer  "tract2010",     limit: 8
    t.float    "xcoord",        limit: 24
    t.float    "ycoord",        limit: 24
    t.string   "zonemap",       limit: 255
    t.string   "zmcode",        limit: 255
    t.string   "sanborn",       limit: 255
    t.float    "taxmap",        limit: 24
    t.string   "edesignum",     limit: 255
    t.float    "appbbl",        limit: 24
    t.datetime "appdate"
    t.integer  "plutomapid",    limit: 8
  end

  create_table "complaint311s", force: :cascade do |t|
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
    t.integer  "unique_key",             limit: 4
  end

  add_index "complaint311s", ["unique_key"], name: "index_r_complaint311s_on_unique_key", unique: true, using: :btree

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
    t.datetime "job_start_date"
    t.string   "job_type",        limit: 255
    t.string   "job_num",         limit: 255
    t.string   "filling_status",  limit: 255
    t.string   "permit_type",     limit: 255
    t.string   "bldg_type",       limit: 255
    t.string   "work_type",       limit: 255
  end

  create_table "dob_violations", force: :cascade do |t|
    t.integer  "property_id",          limit: 4
    t.string   "violation_type",       limit: 255
    t.datetime "created_at",                       null: false
    t.datetime "updated_at",                       null: false
    t.string   "isn_dob_bis_viol",     limit: 255
    t.string   "violation_category",   limit: 255
    t.datetime "issue_date"
    t.datetime "disposition_date"
    t.string   "disposition_comments", limit: 255
  end

  add_index "dob_violations", ["isn_dob_bis_viol"], name: "index_r_dob_violations_on_isn_dob_bis_viol", unique: true, using: :btree

  create_table "hpd_complaints", force: :cascade do |t|
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
    t.datetime "received_date"
    t.integer  "complaint_id",      limit: 4
    t.string   "apartment",         limit: 255
  end

  add_index "hpd_complaints", ["complaint_id"], name: "index_r_hpd_complaints_on_complaint_id", unique: true, using: :btree

  create_table "hpd_violations", force: :cascade do |t|
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
    t.integer  "litigation_id",  limit: 4
    t.datetime "case_open_date"
    t.string   "case_status",    limit: 255
  end

  add_index "litigations", ["litigation_id"], name: "index_r_litigations_on_litigation_id", unique: true, using: :btree

  create_table "owner_properties", force: :cascade do |t|
    t.integer  "property_id", limit: 4
    t.integer  "owner_id",    limit: 4
    t.datetime "created_at",            null: false
    t.datetime "updated_at",            null: false
  end

  create_table "owners", force: :cascade do |t|
    t.string   "name",                        limit: 255
    t.string   "address_line_one",            limit: 255
    t.string   "address_line_two",            limit: 255
    t.string   "city",                        limit: 255
    t.string   "state",                       limit: 255
    t.string   "zipcode",                     limit: 255
    t.datetime "created_at",                              null: false
    t.datetime "updated_at",                              null: false
    t.integer  "corporation_name",            limit: 4
    t.integer  "hpd_registration_id",         limit: 4
    t.integer  "hpd_registration_contact_id", limit: 4
    t.string   "hpd_type",                    limit: 255
  end

  add_index "owners", ["hpd_registration_contact_id"], name: "index_r_owners_on_hpd_registration_contact_id", unique: true, using: :btree

  create_table "properties", force: :cascade do |t|
    t.string   "street_address",      limit: 255
    t.string   "city",                limit: 255
    t.string   "state",               limit: 255
    t.string   "zipcode",             limit: 255
    t.integer  "total_units",         limit: 4
    t.string   "bin",                 limit: 255
    t.boolean  "rent_stabilized"
    t.datetime "created_at",                      null: false
    t.datetime "updated_at",                      null: false
    t.string   "borough",             limit: 255
    t.integer  "block",               limit: 4
    t.integer  "lot",                 limit: 4
    t.integer  "hpd_registration_id", limit: 4
  end

  add_index "properties", ["borough", "block", "lot"], name: "index_r_properties_on_borough_and_block_and_lot", unique: true, using: :btree

end
