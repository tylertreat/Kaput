require.config({
    paths: {
        jquery: 'lib/jQuery/dist/jquery',
        react: 'lib/react/react-with-addons',
        jsx: 'lib/require-jsx/jsx',
        JSXTransformer: 'lib/react/JSXTransformer',
        semantic: 'lib/Semantic-UI/build/packaged/javascript/semantic',
        backbone: 'lib/backbone/backbone',
        underscore: 'lib/underscore/underscore',
        moment: 'lib/moment/moment',
        chosen: 'lib/chosen/chosen.jquery',
        pace: 'lib/pace/pace',
    },

    shim: {
        JSXTransformer: {
            exports: "JSXTransformer"
        },
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
        chosen: {
            deps: ['jquery'],
            exports: 'Chosen'
        },
    }
});

require([
    'jsx!app',
    'semantic',
    'chosen',
], function(App, Semantic) {
    App.initialize();
});

