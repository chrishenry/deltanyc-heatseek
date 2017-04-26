angular
  .module('app')
  .service('OwnerService', OwnerService);

  function OwnerService($http, API_URL) {

  this.getOwner = function (id) {
    return $http.get(API_URL + '/owners/' + id)
  };


};
