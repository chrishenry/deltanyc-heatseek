require 'rails_helper'

describe PropertiesController do
  describe "GET #index" do
    it "returns a successful 200 response" do
       get :index, format: :json
      expect(response).to be_success
    end

    it "returns all properties" do
      FactoryGirl.create_list(:property, 5)
      get :index, format: :json
      parsed_response = JSON.parse(response.body)
      expect(parsed_response.length).to eq(5)
    end    
  end
  
  describe "GET #show" do
    let(:property) { FactoryGirl.create(:property) }

    it "returns a successful 200 response" do
      get :show, id: property, format: :json
      expect(response).to be_success
    end

    it "returns data of an single property" do
      get :show, id: property, format: :json
      parsed_response = JSON.parse(response.body)
      expect(parsed_response).to_not be_nil
    end

    it "returns null if the property does not exist" do
      get :show, id: 200 , format: :json
      expect(response.body).to eq("null")
    end
  end
  
  describe "GET #query" do
    pending
  end
 
    

end