Rails.application.routes.draw do

  root 'home#index'

  resources :properties
  get '/query' => 'properties#query'

  resources :owners  

  resources :complaint311s, only: :index do
    get 'search', on: :collection
  end

  resources :dob_permits, only: :index do
    get 'search', on: :collection
  end

  resources :dob_violations, only: :index do
    get 'search', on: :collection
  end

  resources :hpd_complaints, only: :index do
    get 'search', on: :collection
  end

  resources :hpd_violations, only: :index do
    get 'search', on: :collection
  end

  resources :litigations, only: :index do
    get 'search', on: :collection
  end
end




  