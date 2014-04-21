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

        initialize: function(options) {
            this.dispatcher = options.dispatcher;
            this.reposView = new Dashboard.ReposView({
                dispatcher: this.dispatcher
            });

            this.dispatcher.on('repo:selected', this.showRepo, this);
        },

        render: function() {
            this.$el.html(this.template({user: sessionUser}));
            this.assign(this.reposView, '#repos');
            return this;
        },

        beforeClose: function() {
            this.reposView.close();
            if (this.repoDetailsView) {
                this.repoDetailsView.close();
            }
        },

        showRepo: function(repo) {
            this.repoDetailsView = new Dashboard.RepoDetailsView({model: repo});
            this.assign(this.repoDetailsView, '#repo-details');
        },
    });

    Dashboard.ReposView = BaseView.extend({
        template: Templates.Dashboard.repos(),
        events: {
            'click .sync': 'syncRepos',
        },

        initialize: function(options) {
            this.dispatcher = options.dispatcher;
            var thisView = this;
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
            this.repoViews = _(this.collection.models).map(function(repo) {
                return new Dashboard.RepoView({
                    model: repo,
                    dispatcher: thisView.dispatcher,
                });
            }); 
            var lastSynced = Moment.unix(sessionUser.last_synced).fromNow();
            this.$el.empty();
            this.$el.html(this.template({lastSynced: lastSynced}));

            _(this.repoViews).each(function(repoView) {
                thisView.$('.repos').append(repoView.render().el);
            });

            if (this.repoViews.length > 0) {
                this.repoViews[0].selectRepo();
            }

            return this;
        },

        beforeClose: function() {
            if (this.repoViews) {
                _(this.repoViews).each(function(repoView) {
                    repoView.close();
                });
            }
        },

        syncRepos: function() {
            var thisView = this;
            this.$('.sync').addClass('loading');
            $.ajax({
                url: '/api/v1/user/sync',
                method: 'POST',
                dataType: 'json',
                success: function(user) {
                    sessionUser = user;
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

    Dashboard.RepoView = BaseView.extend({
        template: Templates.Dashboard.repoListItem(),
        events: {
            'click .enable': 'toggleRepo',
            'click': 'selectRepo',
        },

        initialize: function(options) {
            this.dispatcher = options.dispatcher;
        },

        render: function() {
            var html = this.template({repo: this.model.toJSON()});
            var $repo = $(html);
            this.$el.replaceWith($repo);
            this.setElement($repo);
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

        selectRepo: function() {
            this.$el.siblings('.item').removeClass('active');
            this.$el.addClass('active');
            this.dispatcher.trigger('repo:selected', this.model);
        },

    });

    Dashboard.RepoDetailsView = BaseView.extend({
        template: Templates.Dashboard.repoDetails(),

        render: function() {
            this.$el.html(this.template({repo: this.model.toJSON()}));
            return this;
        },

    });

    return Dashboard;
});
