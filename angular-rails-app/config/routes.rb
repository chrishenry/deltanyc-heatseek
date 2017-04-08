Rails.application.routes.draw do

  root 'home#index'

  resources :properties
  get '/query' => 'properties#query'

  resources :owners  

  resources :complaint311s, only: :index 

  resources :dob_permits, only: :index 

  resources :dob_violations, only: :index 

  resources :hpd_complaints, only: :index 

  resources :hpd_violations, only: :index 

  resources :litigations, only: :index 
  
end




  