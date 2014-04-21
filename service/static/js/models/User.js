define([
  'jquery',
  'underscore',
  'backbone',
], function($, _, Backbone) {
    "use strict";

    var User = {};

    User.UserModel = Backbone.Model.extend({
        url: '/api/v1/user'
    });
    
    User.UserCollection = Backbone.Collection.extend({
        model: User.UserModel,
        url: '/api/v1/user',
    });
    
    return User;
});
