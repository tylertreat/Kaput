define([
  'jquery',
  'underscore',
  'backbone',
], function($, _, Backbone) {
    "use strict";

    var Repository = {};

    Repository.RepoModel = Backbone.Model.extend({
        urlRoot: '/api/v1/repository'
    });
    
    DraftCalc.RepoCollection = Backbone.Collection.extend({
        model: Repository.RepoModel,
    });
    
    return DraftCalc;
});

