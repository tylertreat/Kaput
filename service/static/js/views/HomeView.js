define([
  'jquery',
  'underscore',
  'backbone',
  'templates',
  'BaseView',
], function($, _, Backbone, Templates, BaseView) {
    "use strict";

    var HomeView = BaseView.extend({
        template: Templates.Home.index(),

        render: function() {
            this.$el.html(this.template());
            return this;
        }
    });

    return HomeView;
});
