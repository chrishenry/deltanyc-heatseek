angular
    .module('app', ['ui.router', 'templates', 'google.places', 'angularSlideables'])
    .config(function ($stateProvider, $urlRouterProvider) {

      $stateProvider
        .state('home', {
          url: '/', 
          templateUrl: 'home/home.html', 
          controller: 'HomeController as vm',
          onEnter: function(){
            initialize();
          }
        })
        .state('resources', {
          url: '/resources', 
          templateUrl: 'home/resources.html', 
        })
        .state('contact', {
          url: '/contact', 
          templateUrl: 'home/contact.html', 
        })
        .state('owner', {
          url: '/owners/:id', 
          templateUrl: 'owner/owner.html', 
          controller: 'OwnerController as vm'
        })
        .state('property', {
          url: '/properties/:id', 
          templateUrl: 'property/property.html', 
          controller: 'PropertyController as vm'
        });
        

      $urlRouterProvider.otherwise('/');

    });
