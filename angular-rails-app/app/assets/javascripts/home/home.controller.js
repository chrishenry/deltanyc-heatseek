angular
  .module('app')
  .controller('HomeController', ['$scope', 'HomeService', '$state','$http', HomeController])

function HomeController($scope, HomeService, $state,$http) {
  var vm = this;


//********** Properties Data *************//

  $scope.place = null;
  $scope.autocompleteOptions = {
      componentRestrictions: { country: 'us'}, // political: "New York", country: 'us',
      types: ['geocode']
  }

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
      if((propertyData.data[0]!= undefined) && (propertyData.data[0].id)){
        $state.go('property', {id: propertyData.data[0].id})
      }
      else{
        vm.addressError();
      }
    }, function(error){
      alert('Unable to get property' + error.statusText);
    });
 }


 vm.addressError = function() {
      vm.alerts = [{msg: 'Address not found in database.  Perhaps try another variation.'}];
    };

 vm.closeAlert = function() {
     vm.alerts = [];
    };


 //************ Owners data ***************//  

 vm.selectedOwner = ''

  vm.getOwners = function(input) {
    var limit = 6;
    return HomeService.getOwners(input).then(function(res){
        var owners = [];
        var lim = Math.min(limit,res.data.length);
        for (var i = 0; i < lim; i++) {
          owners.push(res.data[i]);
        }
        return owners;
    });
  };
}
