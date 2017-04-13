var API_URL ='http://localhost:3000'

angular
  .module('app')
  .service('PropertyService', PropertyService);

  function PropertyService($http) {
  
  this.getProperty = function (id) {
    return $http.get(API_URL + '/properties/' + id)
  };

  this.getComplaint311s = function (id, pageNumber){
    return $http.get(API_URL + '/complaint311s?' + 'property_id=' + id + '&page=' + pageNumber)
  }

  this.getDobPermits = function (id, pageNumber){
    return $http.get(API_URL + '/dob_permits?' + 'property_id=' + id + '&page=' + pageNumber)
  }

  this.getDobViolations = function (id, pageNumber){
    return $http.get(API_URL + '/dob_violations?' + 'property_id=' + id + '&page=' + pageNumber)
  }

  this.getHpdComplaints = function (id, pageNumber){
    return $http.get(API_URL + '/hpd_complaints?' + 'property_id=' + id + '&page=' + pageNumber)
  }

  this.getHpdViolations = function (id, pageNumber){
    return $http.get(API_URL + '/hpd_violations?' + 'property_id=' + id + '&page=' + pageNumber)
  }

  this.getLitigations = function (id, pageNumber){
    return $http.get(API_URL + '/litigations?' + 'property_id=' + id + '&page=' + pageNumber)
  }
  
 
};