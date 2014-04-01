define([
  'jquery',
  'underscore',
  'backbone',
], function($, _, Backbone) {
    "use strict";

    var BaseView = Backbone.View.extend({

        close: function() {
            if (this.beforeClose) {
                this.beforeClose();
            }
            this.remove();
            this.unbind();
        },

        assign: function(view, selector) {
            view.setElement(this.$(selector)).render();
        },

    });

    return BaseView;
});
