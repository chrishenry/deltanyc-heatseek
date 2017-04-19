var API_URL =''

angular
  .module('app')
  .service('PropertyService', PropertyService);

  function PropertyService($http) {

  this.getProperty = function (id) {
    return $http.get(API_URL + '/properties/' + id)
  };


};
