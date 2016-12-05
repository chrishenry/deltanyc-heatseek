angular 
  .module('app')
  .controller('HomeController', HomeController)

function HomeController(HomeService) {
  var vm = this;

  vm.place =''     
  
}


HomeController.$inject = ['HomeService'];