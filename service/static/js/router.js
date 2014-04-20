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
            if (loggedIn) {
                this.dashboard();
            } else {
                this.showView('#container', new HomeView());
            }
        },

        dashboard: function() {
            if (loggedIn) {
                this.showView('#container', new DashboardView.DashboardView());
            } else {
                this.index();
            }
        },

        showView: function(selector, view) {
            if (this.currentView) {
                this.currentView.close();
            }

            $(selector).html(view.render().el);
            this.currentView = view;
            return view;
        },
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
