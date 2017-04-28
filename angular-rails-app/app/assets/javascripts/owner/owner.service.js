angular
  .module('app')
  .service('OwnerService', OwnerService);

  function OwnerService($http, ENV) {

  this.getOwner = function (id) {
    return $http.get(ENV.API_URL + '/owners/' + id)
  };


};
