define([
  'jquery',
  'underscore',
  'backbone',
  'moment',
  'templates',
  'BaseView',
  'Repository',
], function($, _, Backbone, Moment, Templates, BaseView, Repository) {
    "use strict";

    var Dashboard = {};

    Dashboard.DashboardView = BaseView.extend({
        template: Templates.Dashboard.dashboard(),

        initialize: function() {
            this.reposView = new Dashboard.ReposView();
        },

        render: function() {
            this.$el.html(this.template({user: sessionUser}));
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
        events: {
            'click .sync': 'syncRepos',
        },

        initialize: function() {
            var thisView = this;
            this.repoViews = [];
            this.collection = new Repository.RepoCollection();
            this.collection.fetch({
                reset: true,
                success: function(collection) {
                    if (collection.length === 0) {
                        thisView.syncRepos();
                    } else {
                        thisView.render();
                    }
                },
            });
        },

        render: function() {
            var thisView = this;
            this.collection.each(function(repo) {
                thisView.repoViews.push(new Dashboard.RepoView({model: repo}));
            }); 
            var lastSynced = Moment.unix(sessionUser.last_synced).fromNow();
            this.$el.empty();
            this.$el.html(this.template({lastSynced: lastSynced}));

            _(this.repoViews).each(function(repoView) {
                thisView.$('.repos').append(repoView.render().el);
            });

            return this;
        },

        syncRepos: function() {
            var thisView = this;
            this.$('.sync').addClass('loading');
            $.ajax({
                url: '/api/v1/user/sync',
                method: 'POST',
                dataType: 'json',
                success: function(user) {
                    var repos = user.repos;
                    thisView.collection = new Repository.RepoCollection(repos);
                    thisView.render();
                },
                complete: function() {
                    thisView.$('.sync').removeClass('loading');
                },
            });
        },
    });

    Dashboard.RepoView = Backbone.View.extend({
        template: Templates.Dashboard.repoListItem(),
        events: {
            'click .enable': 'toggleRepo'
        },

        render: function() {
            this.$el.empty();
            this.$el.html(this.template({repo: this.model.toJSON()}));
            return this;
        },

        toggleRepo: function() {
            var thisView = this;
            var enabled = !this.model.get('enabled');
            this.toggleEnabledButton(enabled);
            this.model.save({'enabled': enabled}, {
                error: function() {
                    thisView.toggleEnabledButton(!enabled);
                }
            });
        },

        toggleEnabledButton: function(enabled) {
            var $toggle = this.$('.enable');
            if (enabled) {
                $toggle.addClass('active');
            } else {
                $toggle.removeClass('active');
            }
        },

    });

    return Dashboard;
});
