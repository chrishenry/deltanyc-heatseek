angular
  .module('app')
  .controller('OwnerController', OwnerController);

OwnerController.$inject = ['OwnerService', 'owner'];


function OwnerController(OwnerService, owner) {
  var vm = this;  
  vm.data = owner.data;
}