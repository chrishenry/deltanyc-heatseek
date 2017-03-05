module.exports = function(config) {
  config.set({
    frameworks: ['jasmine'],

    files: [
      {pattern: "test/*.js", watched: false}
    ],

    preprocessors: {
      "test/*.js": ['webpack', 'sourcemap']
    },

    webpack: {
      entry: {
        'application.js': './app/assets/javascripts/application.js'
      },
      output: {},
      module: {
        preLoaders: [
          {
            loader: 'sprockets-loader',
            query: {
              logicalPaths: [
                'app/assets'
              ]
            }
          }
        ]
      },
      devtool: 'inline-source-map'
    },

    reporters: ['progress', 'kjhtml'],

    port: 9876,

    colors: true,

    logLevel: config.LOG_INFO,

    autoWatch: true,

    browsers: ['PhantomJS'],

    singleRun: false,

    concurrency: Infinity
  });
};
