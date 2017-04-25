class InitSchema < ActiveRecord::Migration
  def up

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
      t.string   "permit_status",   limit: 255
      t.datetime "filing_date"
      t.datetime "expiration_date"
      t.datetime "created_at",                  null: false
      t.datetime "updated_at",                  null: false
      t.string   "work_type",       limit: 255
      t.datetime "job_start_date"
      t.string   "job_type",        limit: 255
      t.string   "job_num",         limit: 255
      t.string   "filing_status",  limit: 255
      t.string   "permit_type",     limit: 255
      t.string   "bldg_type",       limit: 255
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
      t.string   "corporation_name",            limit: 255
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
      t.integer  "rent_stabilized",     limit: 4
      t.datetime "created_at",                      null: false
      t.datetime "updated_at",                      null: false
      t.string   "borough",             limit: 255
      t.integer  "block",               limit: 4
      t.integer  "lot",                 limit: 4
      t.integer  "bbl",                 limit: 8
      t.integer  "hpd_registration_id", limit: 4
    end

    add_index "properties", ["borough", "block", "lot"], name: "index_r_properties_on_borough_and_block_and_lot", unique: true, using: :btree
    add_index "properties", ["bbl"], name: "index_r_properties_on_bbl", using: :btree
    add_index "properties", ["street_address", "zipcode"], name: "index_r_properties_on_street_address_and_zipcode", using: :btree

  end

  def down
    raise ActiveRecord::IrreversibleMigration, "The initial migration is not revertable"
  end
end
