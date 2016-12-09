50.times do
     Property.create(
        street_address: FFaker::AddressUS.street_address,
        city: FFaker::AddressUS.city,
        state: FFaker::AddressUS.state_abbr,
        zipcode: FFaker::AddressUS.zip_code,
        total_units: rand(5..200),
        rent_stabilized: FFaker::Boolean.random,
      ) 
end 

50.times do
     Owner.create(
        name: FFaker::Name.name,
        address_line_one: FFaker::AddressUS.street_address,
        address_line_two: FFaker::AddressUS.secondary_address,
        city: FFaker::AddressUS.city,
        state: FFaker::AddressUS.state_abbr,
        zipcode: FFaker::AddressUS.zip_code
      ) 
end 

50.times do
    OwnerProperty.create(
      owner_id: rand(1..20),  
      property_id: rand(1..20)
      )
  end


