require.config({
    paths: {
        jquery: 'lib/jquery-1.11.0.min',
        underscore: 'lib/underscore-min',
        backbone: 'lib/backbone-min',
        semantic: 'lib/semantic.min',
        handlebars: 'lib/handlebars-1.3.0',
        text: 'lib/text',

        BaseView: 'views/BaseView',
        HomeView: 'views/HomeView',
        DashboardView: 'views/DashboardView',
    },
    shim: {
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        underscore: {
            exports: '_'
        },
        semantic: {
            exports: 'Semantic'
        },
        handlebars: {
            exports: 'Handlebars'
        },
    }
});

require([
    'router',
], function(Router) {
    Router.initialize();
});

