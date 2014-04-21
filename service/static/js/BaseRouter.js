define([
    'jquery',
    'underscore',
    'backbone',
], function($, _, Backbone) {
    "use strict";

    var BaseRouter = Backbone.Router.extend({

        showView: function(selector, view) {
            if (this.currentView) {
                this.currentView.close();
            }

            $(selector).html(view.render().el);
            this.currentView = view;
            return view;
        },

    });

    return BaseRouter;
});
