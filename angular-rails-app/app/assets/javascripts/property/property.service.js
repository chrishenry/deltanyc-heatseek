angular
  .module('app')
  .service('PropertyService', PropertyService);

  function PropertyService($http, ENV) {

  this.getProperty = function (id) {
    return $http.get(ENV.API_URL + '/properties/' + id)
  };

  this.getTableInfo = function (id, pageNumber, resource){
    return $http.get(ENV.API_URL + '/' + resource + '?' + 'property_id=' + id + '&page=' + pageNumber)
  } 
};

