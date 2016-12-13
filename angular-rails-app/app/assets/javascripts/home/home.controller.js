angular
  .module('app')
  .controller('HomeController', ['$scope', 'HomeService', HomeController])

function HomeController($scope, HomeService) {
  var vm = this;

  vm.place ='';

  vm.componentForm = {
    street_number: 'short_name',
    route: 'long_name',
    locality: 'long_name',
    administrative_area_level_1: 'short_name',
    country: 'long_name',
    postal_code: 'short_name'
  };

  vm.mapping = {
    street_number: 'number',
    route: 'street',
    locality: 'city',
    administrative_area_level_1: 'state',
    country: 'country',
    postal_code: 'zip'
  };

  vm.details = {};

  vm.setDetails = function() {
    if (vm.place.address_components) {
      for (var i = 0; i < vm.place.address_components.length; i++) {
        var addressType = vm.place.address_components[i].types[0];
        if (vm.componentForm[addressType]) {
            var val = vm.place.address_components[i][vm.componentForm[addressType]];
            vm.details[vm.mapping[addressType]] = val;
        }
      }
    }

  };

  $scope.$watch('vm.place',vm.setDetails);


 vm.getProperty = function(){
    HomeService.getProperty(vm.details)
    .then(function(propertyData){
      console.log(propertyData);
    }, function(error){
      alert('Unable to get property' + error.statusText);
    });
 }




}
