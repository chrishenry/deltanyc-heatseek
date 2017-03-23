angular
  .module('app')
  .controller('OwnerController', OwnerController);

OwnerController.$inject = ['OwnerService', '$stateParams', '$state', 'owner'];


function OwnerController(OwnerService, $stateParams, $state, owner) {
  var vm = this;  
  vm.data = owner.data;
}