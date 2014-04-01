define([
  'jquery',
  'underscore',
  'backbone',
  'templates',
  'BaseView',
], function($, _, Backbone, Templates, BaseView) {
    "use strict";

    var Dashboard = {};

    Dashboard.DashboardView = BaseView.extend({
        template: Templates.Dashboard.dashboard(),

        initialize: function() {
            this.reposView = new Dashboard.ReposView();
        },

        render: function() {
            this.$el.html(this.template());
            this.assign(this.reposView, '#repos');
            return this;
        },

        close: function() {
            this.reposView.remove();
            this.remove();
        }
    });

    Dashboard.ReposView = Backbone.View.extend({
        template: Templates.Dashboard.repos(),

        render: function() {
            this.$el.html(this.template());
            return this;
        }
    });

    return Dashboard;
});
