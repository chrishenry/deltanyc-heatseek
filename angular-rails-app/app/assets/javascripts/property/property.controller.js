angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService','property'];


function PropertyController(PropertyService, property) {
  var vm = this;  
  vm.data = property.data;
  vm.itemsPerPage = 10;

  vm.hpdViolations =[];
  vm.hpdComplaints =[];
  vm.dobPermits =[];
  vm.dobViolations =[];
  vm.litigations =[];
  vm.complaint311s =[];

  vm.hpdViolationsPageChanged = function(newPage) {
    getHpdViolations(newPage);
  };

  vm.hpdComplaintsPageChanged = function(newPage) {
    getHpdComplaints(newPage);
  };

  vm.dobPermitsPageChanged = function(newPage) {
    getDobPermits(newPage);
  };

  vm.dobViolationsPageChanged = function(newPage) {
    getDobViolations(newPage);
  };

  vm.litigationsPageChanged = function(newPage) {
    getLitigations(newPage);
  };

  vm.complaint311sPageChanged = function(newPage) {
    getComplaint311s(newPage);
  };

  function getHpdViolations(pageNumber) {
    return PropertyService.getHpdViolations(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.hpdViolations = result.data.hpd_violations;
      vm.totalHpdViolations = result.data.meta.total_count
      vm.hpdViolationsPage = result.data.meta.current_page
      });
    }

   function getHpdComplaints(pageNumber) {
    return PropertyService.getHpdComplaints(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.hpdComplaints = result.data.hpd_complaints;
      vm.totalHpdComplaints = result.data.meta.total_count
      vm.hpdComplaintsPage = result.data.meta.current_page
      });
    }
    
    function getDobPermits(pageNumber) {
    return PropertyService.getDobPermits(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.dobPermits = result.data.dob_permits;
      vm.totalDobPermits = result.data.meta.total_count
      vm.dobPermitsPage = result.data.meta.current_page
      });
    }

    function getDobViolations(pageNumber) {
    return PropertyService.getDobViolations(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.dobViolations = result.data.dob_violations;
      vm.totalDobViolations = result.data.meta.total_count
      vm.dobViolationsPage = result.data.meta.current_page
      });
    }

    function getLitigations(pageNumber) {
    return PropertyService.getLitigations(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.litigations = result.data.litigations;
      vm.totalLitigations = result.data.meta.total_count
      vm.litigationsPage = result.data.meta.current_page
      });
    }

    function getComplaint311s(pageNumber) {
    return PropertyService.getComplaint311s(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.complaint311s = result.data.complaint311s;
      vm.totalComplaint311s = result.data.meta.total_count
      vm.complaint311sPage = result.data.meta.current_page
      });
    } 

    getComplaint311s(1)
    getDobPermits(1)
    getDobViolations(1)
    getHpdComplaints(1)
    getHpdViolations(1)
    getLitigations(1)
}

