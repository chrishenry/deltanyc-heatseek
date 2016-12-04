angular
    .module('app', ['ui.router', 'templates'])
    .config(function ($stateProvider, $urlRouterProvider) {

      $stateProvider
        .state('home', {
          url: '/', 
          templateUrl: 'home/home.html', 
          controller: 'HomeController as vm'
        });
        

      $urlRouterProvider.otherwise('/');

    });
