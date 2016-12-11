var API_URL ='http://localhost:3000'

angular
  .module('app')
  .service('PropertyService', PropertyService);

  function PropertyService($http) {
  
  this.getProperty = function (id) {
    return $http.get(API_URL + '/properties/' + id)
  };
  
 
};