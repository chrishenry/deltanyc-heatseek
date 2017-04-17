var API_URL =''

angular
  .module('app')
  .service('HomeService', HomeService);

  function HomeService($http) {

  this.getProperty = function (details) {
    return $http.get(API_URL + '/query?' + $.param({
            street_address: details.number + ' ' + details.street,
            city: details.city,
            state: details.state,
            zipcode: details.zip
        }));
  }


  this.getOwners = function (input){
    return $http.get(API_URL + '/owners?' + $.param({
            name: input
        }));
  }



};
