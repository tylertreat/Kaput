define([
  'jquery',
  'underscore',
  'backbone',
], function($, _, Backbone) {
    "use strict";

    var Repository = {};

    Repository.RepoModel = Backbone.Model.extend({
        url: '/api/v1/repo'
    });
    
    Repository.RepoCollection = Backbone.Collection.extend({
        model: Repository.RepoModel,
        url: '/api/v1/repo',

        enabled: function() {
            var repos = this.select(function(repo) {
                return repo.get('enabled');
            });

            return new Repository.RepoCollection(repos);
        }
    });
    
    return Repository;
});

