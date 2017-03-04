require 'rails_helper'

RSpec.describe Property, type: :model do
  it "has a valid factory" do
     expect(FactoryGirl.create(:property)).to be_instance_of(Property)
  end

  it "returns a property's full address as a string" do
    property = FactoryGirl.create(:property, street_address: "2143 N. Shore Dr.",
    city: "Holland", state: "MI", zipcode: "49508")
    puts "HERERERER property.full_address"
    puts property.full_address
    Rails.logger.debug variable.inspect property
    Rails.logger.debug variable.inspect property.full_address

    sdgfs dfg

    expect(property.full_adess).to eq("2143 N. Shore Dr., Holland, MI 49508")
  end

   it "returns a property's expanded borough name" do
     property = (FactoryGirl.create(:property, borough: "BK"))
     expect(property.expand_borough).to eq("BROOKLYN")
  end

end


