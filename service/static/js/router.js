define([
    'jquery',
    'underscore',
    'backbone',
    'HomeView',
    'DashboardView',
    'AccountView',
    'User',
], function($, _, Backbone, HomeView, DashboardView, AccountView, User) {

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'index',
            'dashboard': 'dashboard',
            'account': 'account',
        },

        initialize: function() {
            this.dispatcher = _.clone(Backbone.Events);
        },

        index: function() {
            if (sessionData && sessionData.is_authenticated) {
                this.dashboard();
            } else {
                this.showView('#container', new HomeView());
            }
        },

        dashboard: function() {
            if (sessionData && sessionData.is_authenticated) {
                this.showView('#container', new DashboardView.DashboardView({
                    dispatcher: this.dispatcher
                }));
            } else {
                this.index();
            }
        },

        account: function() {
            if (sessionData && sessionData.is_authenticated) {
                this.showView('#container', new AccountView.AccountSettingsView({
                    model: new User.UserModel(sessionData)
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
