var API_URL = ''

angular
  .module('app')
  .service('OwnerService', OwnerService);

  function OwnerService($http) {

  this.getOwner = function (id) {
    return $http.get(API_URL + '/owners/' + id)
  };


};
