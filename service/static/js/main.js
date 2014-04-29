require.config({
    paths: {
        jquery: 'lib/jquery-1.11.0.min',
        underscore: 'lib/underscore-min',
        backbone: 'lib/backbone-min',
        semantic: 'lib/semantic.min',
        handlebars: 'lib/handlebars-1.3.0',
        text: 'lib/text',
        moment: 'lib/moment.min',
        chosen: 'lib/chosen.jquery.min',
        pace: 'lib/pace.min',

        BaseView: 'views/BaseView',
        HomeView: 'views/HomeView',
        DashboardView: 'views/DashboardView',
        Repository: 'models/Repository',
        User: 'models/User',
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
            deps: ['jquery'],
            exports: 'Semantic'
        },
        handlebars: {
            exports: 'Handlebars'
        },
        chosen: {
            deps: ['jquery'],
            exports: 'Chosen'
        },
    }
});

require([
    'router',
    'semantic',
    'chosen',
    'pace',
], function(Router, Semantic, Chosen, Pace) {
    Router.initialize();
    Pace.start({ajax: {trackMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']}});

    $('.ui.dropdown').dropdown();
});

