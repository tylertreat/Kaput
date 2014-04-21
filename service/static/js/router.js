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

        initialize: function() {
            this.dispatcher = _.clone(Backbone.Events);
        },

        index: function() {
            if (sessionUser && sessionUser.is_authenticated) {
                this.dashboard();
            } else {
                this.showView('#container', new HomeView());
            }
        },

        dashboard: function() {
            if (sessionUser && sessionUser.is_authenticated) {
                this.showView('#container', new DashboardView.DashboardView({
                    dispatcher: this.dispatcher
                }));
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
