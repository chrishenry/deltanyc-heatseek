var API_URL ='http://localhost:3000'

angular
  .module('app')
  .service('OwnerService', OwnerService);

  function OwnerService($http) {
  
  this.getOwner = function (id) {
    return $http.get(API_URL + '/owners/' + id)
  };
  
 
};