var API_URL ='http://localhost:3000'

angular
  .module('app')
  .service('HomeService', HomeService);

  function HomeService($http) {
  
  this.getProperties = function () {
    return $http.get(API_URL + '/properties')
  };
 
};