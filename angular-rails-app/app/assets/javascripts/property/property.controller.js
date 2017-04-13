angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService','property'];


function PropertyController(PropertyService, property) {
  var vm = this;  
  vm.data = property.data;
  vm.itemsPerPage = 10;
  vm.litigations =[];

  vm.litigationsPageChanged = function(newPage) {
    getLitigationsPage(newPage);
  };

  function getLitigationsPage(pageNumber) {
    return PropertyService.getLitigations(vm.data.id, pageNumber)    
    .then(function(result) {
      vm.litigations = result.data.litigations;
      vm.totalLitigations = result.data.meta.total_count
      vm.litigationPage = result.data.meta.current_page
      });
    }

    getLitigationsPage(1)
}

