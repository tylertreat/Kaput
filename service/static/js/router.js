define([
    'jquery',
    'underscore',
    'backbone',
    'HomeView',
    'DashboardView',
], function($, _, Backbone, HomeView, DashboardView) {

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'index',
            'dashboard': 'dashboard'
        },

        index: function() {
            this.loadView(new HomeView());
        },

        dashboard: function() {
            this.loadView(new DashboardView.DashboardView());
        },

        loadView: function(view) {
            this.view && (this.view.close ? this.view.close() : this.view.remove());
            this.view = view;
        }
    });

    var initialize = function() {
        var appRouter = new AppRouter;
        var dispatcher = _.clone(Backbone.Events);

        Backbone.history.start();
    };

    return { 
        initialize: initialize
    };
});
