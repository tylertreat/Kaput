define([
  'jquery',
  'underscore',
  'backbone',
  'templates',
], function($, _, Backbone, Templates) {
    "use strict";

    var HomeView = Backbone.View.extend({
        el: $('#container'),
        template: Templates.Home.index(),

        initialize: function() {
            this.render();
        },

        render: function() {
            this.$el.html(this.template);
        }
    });

    return HomeView;
});
