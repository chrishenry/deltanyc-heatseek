angular 
  .module('app')
  .controller('PropertyController', PropertyController)

function PropertyController(PropertyService) {
  var vm = this;
    
  
}


PropertyController.$inject = ['PropertyService'];