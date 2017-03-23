angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService', '$stateParams', '$state', 'property'];


function PropertyController(PropertyService, $stateParams, $state, property) {
  var vm = this;  
  vm.data = property.data;
}

