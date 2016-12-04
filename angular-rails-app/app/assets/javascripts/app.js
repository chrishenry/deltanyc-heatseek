angular
    .module('app', ['ui.router', 'templates', 'ui.bootstrap'])
    .config(function ($stateProvider, $urlRouterProvider) {

      $stateProvider
        .state('home', {
          url: '/', 
          templateUrl: 'home/home.html', 
          controller: 'HomeController as vm'
        });
        

      $urlRouterProvider.otherwise('/');

    });
