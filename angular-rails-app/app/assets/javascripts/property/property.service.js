var API_URL =''

angular
  .module('app')
  .service('PropertyService', PropertyService);

  function PropertyService($http) {

  this.getProperty = function (id) {
    return $http.get(API_URL + '/properties/' + id)
  };

  this.getTableInfo = function (id, pageNumber, resource){
    return $http.get(API_URL + '/' + resource + '?' + 'property_id=' + id + '&page=' + pageNumber)
  } 
};

