angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService','property'];


function PropertyController(PropertyService, property) {
  var vm = this;  
  vm.data = property.data;
  vm.itemsPerPage = 10;

  vm.tables = {
    'complaint311s': {
      'data': [],
      'urlResource': 'complaint311s',
      'total': undefined,
      'page': 1
    },
    'dobPermits': {
      'data': [],
      'urlResource': 'dob_permits',
      'total': undefined,
      'page': 1
    },
    'dobViolations': {
      'data': [],
      'urlResource': 'dob_violations',
      'total': undefined,
      'page': 1
    },
    'hpdComplaints': {
      'data': [],
      'urlResource': 'hpd_complaints',
      'total': undefined,
      'page': 1
    },
    'hpdViolations': {
      'data': [],
      'urlResource': 'hpd_violations',
      'total': undefined,
      'page': 1
    },
    'litigations': {
      'data': [],
      'urlResource': 'litigations',
      'total': undefined,
      'page': 1
    }    
  }; 


  function getTableInfo(pageNumber, resource) {
    return PropertyService.getTableInfo(vm.data.id, pageNumber, tables[resource]['urlResource'])    
    .then(function(result) {
      vm.tables[resource]['data'] = result.data.(vm.tables[resource]['urlResource']); //need underscore rather than camelCase
      vm.tables[resource]['total'] = result.data.meta.total_count
      vm.tables[resource]['page'] = result.data.meta.current_page
    });
  }

   
    getTableInfo(1, "complaint311s")
    getTableInfo(1, "dobPermits")
    getTableInfo(1, "dobViolations")
    getTableInfo(1, "hpdComplaints")
    getTableInfo(1, "hpdViolations")
    getTableInfo(1, "litigations")
}

