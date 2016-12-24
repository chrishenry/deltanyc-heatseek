angular
  .module('app')
  .controller('OwnerController', OwnerController);

OwnerController.$inject = ['OwnerService', '$stateParams', '$state'];


function OwnerController(OwnerService, $stateParams, $state) {
  var vm = this
  

  vm.getOwner = function(){
    OwnerService.getOwner($stateParams.id)
    .then(function(owner){
      vm.data = owner.data;
    }, function(error){
        alert('Unable to get owner data: ' + error.statusText);
    })
  }

  vm.getOwner();  

}