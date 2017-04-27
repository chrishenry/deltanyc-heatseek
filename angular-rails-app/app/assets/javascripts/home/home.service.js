angular
  .module('app')
  .service('HomeService', HomeService);

  function HomeService($http, ENV) {

  this.getProperty = function (details) {
    return $http.get(ENV.API_URL + '/query?' + $.param({
            street_address: details.number + ' ' + details.street,
            city: details.city,
            state: details.state,
            zipcode: details.zip
        }));
  }


  this.getOwners = function (input){
    return $http.get(ENV.API_URL + '/owners?' + $.param({
            name: input
        }));
  }



};
