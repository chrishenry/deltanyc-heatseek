angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService','property'];


function PropertyController(PropertyService, property) {
  var vm = this;  
  vm.property = property.data;
  vm.itemsPerPage = 10;

  vm.tables = {
    'complaint311s' : new Table("complaint311s"),
    'dobPermits' : new Table("dob_permits"),
    'dobViolations' : new Table("dob_violations"),
    'hpdComplaints' : new Table("hpd_complaints"),
    'hpdViolations' : new Table("hpd_violations"),
    'litigations' : new Table("litigations")
  }

  function Table(urlResource) {
    this.data = [];
    this.urlResource = urlResource;
    this.total = undefined;
    this.page = 1;
  }

  vm.getTableInfo = function(pageNumber, tableName) {
    return PropertyService.getTableInfo(vm.property.id, pageNumber, vm.tables[tableName]['urlResource'])    
    .then(function(result) {
      var underscoreName = vm.tables[tableName]['urlResource']; //need for Rails endpoints
      vm.tables[tableName]['data'] = result.data[underscoreName]; 
      vm.tables[tableName]['total'] = result.data.meta.total_count
      vm.tables[tableName]['page'] = result.data.meta.current_page
    });
  }

  function initializeTables(){
    Object.keys(vm.tables).forEach(function (tableName) {
      vm.getTableInfo(1, tableName)
    });
  }

  initializeTables()  
}

