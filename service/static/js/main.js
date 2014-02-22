require.config({
    paths: {
        jquery: 'lib/jquery-1.11.0.min',
        underscore: 'lib/underscore-min',
        backbone: 'lib/backbone-min',
        bootstrap: 'lib/bootstrap.min',
        handlebars: 'lib/handlebars-1.3.0',
        text: 'lib/text',
    },
    shim: {
        backbone: {
            deps: ['underscore', 'jquery'],
            exports: 'Backbone'
        },
        underscore: {
            exports: '_'
        },
        bootstrap: {
            deps: ["jquery"],
            exports: 'bootstrap'
        },
        handlebars: {
            exports: 'Handlebars'
        },
    }
});

require([
    'router',
    'jquery',
    'underscore',
    'backbone',
    'bootstrap',
    'handlebars',
], function(Router, $, _, Backbone, Bootstrap, Handlebars) {
    Router.initialize();
});

