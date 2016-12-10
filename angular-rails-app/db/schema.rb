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

ActiveRecord::Schema.define(version: 20161209024622) do

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
  end

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
    t.datetime "created_at",                  null: false
    t.datetime "updated_at",                  null: false
  end

end
