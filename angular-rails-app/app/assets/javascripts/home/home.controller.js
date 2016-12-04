angular 
  .module('app')
  .controller('HomeController', HomeController)

function HomeController(HomeService) {
  var vm = this;

  vm.search = ''

  vm.getProperties = function(){
    HomeService.getProperties()
    .then(function(properties){
      vm.data = properties.data;
    }, function(error){
        alert('Unable to get properties: ' + error.statusText);
    })
  }

  vm.getProperties();  
     
  
}


HomeController.$inject = ['HomeService'];