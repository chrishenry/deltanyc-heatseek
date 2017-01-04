angular
  .module('app')
  .controller('PropertyController', PropertyController);

PropertyController.$inject = ['PropertyService', '$stateParams', '$state'];


function PropertyController(PropertyService, $stateParams, $state) {
  var vm = this
  

  vm.getProperty = function(){
    PropertyService.getProperty($stateParams.id)
    .then(function(property){
      vm.data = property.data;
    }, function(error){
        alert('Unable to get property data: ' + error.statusText);
    })
  }

  vm.getProperty();  

}

