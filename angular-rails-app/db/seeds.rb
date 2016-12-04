50.times do
     Property.create(
        street_address: FFaker::AddressUS.street_address,
        city: FFaker::AddressUS.city,
        state: FFaker::AddressUS.state_abbr,
        zipcode: FFaker::AddressUS.zip_code,
        total_units: rand(5..200),
        rent_stabilized: FFaker::Boolean.random,
        owner_id: rand(1..10)
      ) 
end 


