define([
    'jquery',
    'underscore',
    'backbone',
], function($, _, Backbone) {

    var AppRouter = Backbone.Router.extend({
        routes: {
            "": "showIndexPage"
        }
    });

    var initialize = function() {
        var appRouter = new AppRouter;
        var dispatcher = _.clone(Backbone.Events);

        appRouter.on('route:showIndexPage', function() {

        });

        Backbone.history.start();
    };

    return { 
        initialize: initialize
    };
});
