FactoryGirl.define do
  factory :property do |f|
    f.street_address{FFaker::AddressUS.street_address} 
    f.city {FFaker::AddressUS.city}
    f.state {FFaker::AddressUS.state_abbr}
    f.zipcode {FFaker::AddressUS.zip_code}
    f.total_units {rand(5..200)}
    f.rent_stabilized {FFaker::Boolean.random}
  end

  factory :invalid_property, parent: :property do |f|
    f.street_address nil
  end
end

