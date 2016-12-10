var API_URL ='http://localhost:3000'

angular
  .module('app')
  .service('HomeService', HomeService);

  function HomeService($http) {
  
  this.getProperty = function (details) {
    return $http.post(API_URL + '/query', {
        street_address: details.number + ' ' + details.street,
        city: details.city,
        state: details.state,
        zipcode: details.zip
    });
  };
 


};
