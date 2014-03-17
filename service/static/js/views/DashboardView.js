define([
  'jquery',
  'underscore',
  'backbone',
  'templates',
], function($, _, Backbone, Templates) {
    "use strict";

    var Dashboard = {};

    Dashboard.DashboardView = Backbone.View.extend({
        el: $('#container'),
        template: Templates.Dashboard.dashboard(),

        initialize: function() {
            this.render();
            this.reposView = new Dashboard.ReposView({
                el: this.$('#repos')
            });
        },

        render: function() {
            this.$el.html(this.template);
        },

        close: function() {
            this.reposView.remove();
            this.remove();
        }
    });

    Dashboard.ReposView = Backbone.View.extend({
        template: Templates.Dashboard.repos(),

        initialize: function() {
            this.render();
        },

        render: function() {
            this.$el.html(this.template);
        }
    });

    return Dashboard;
});
