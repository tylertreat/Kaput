define([
  'jquery',
  'underscore',
  'backbone',
  'moment',
  'templates',
  'BaseView',
  'Repository',
  'User',
], function($, _, Backbone, Moment, Templates, BaseView, Repository, User) {
    "use strict";

    var Dashboard = {};

    Dashboard.DashboardView = BaseView.extend({
        template: Templates.Dashboard.dashboard(),
        events: {
            'change .repo-select': 'changeActiveRepo',
            'click .sync': 'sync',
        },

        initialize: function(options) {
            var thisView = this;
            this.dispatcher = options.dispatcher;
            this.sessionUser = new User.UserModel(sessionData);
            this.collection = new Repository.RepoCollection();
            this.dispatcher.on('repo:selected', this.showRepo, this);
        },

        render: function() {
            var thisView = this;
            this.collection.fetch({
                reset: true,
                success: function(collection) {
                    if (collection.length === 0) {
                        thisView.sync();
                    } else {
                        thisView._render();
                    }
                },
            });
            return this;
        },

        _render: function() {
            var lastSynced = Moment.unix(this.sessionUser.get('last_synced')).fromNow();
            this.$el.html(this.template({
                user: this.sessionUser.toJSON(),
                repos: this.collection.toJSON(),
                lastSynced: lastSynced,
            }));

            // Select the last active repo. If there isn't one, select the
            // first in the list.
            var activeRepoId = this.sessionUser.get('active_repo');
            if (!activeRepoId) {
                activeRepoId = this.collection.first().get('id');
            }

            this.$('.repo-select').val(activeRepoId);
            this.$('.repo-select').chosen();
            this.selectRepo(activeRepoId);

            return this;
        },

        beforeClose: function() {
            if (this.repoView) {
                this.repoView.close();
            }
        },

        // Change the user's active repo. This is the repo that will be shown on
        // page load. Also display it in the dashboard.
        changeActiveRepo: function(e) {
            var repoId = $(e.target).val();
            this.sessionUser.save({'active_repo': repoId});
            this.selectRepo(repoId);
        },

        // Display the selected repo in the dashboard.
        selectRepo: function(repoId) {
            var repo = this.collection.findWhere({id: repoId});

            if (!repo) {
                return;
            }

            if (this.repoView) {
                this.repoView.undelegateEvents();
            }
            this.repoView = new Dashboard.RepoView({model: repo});
            this.assign(this.repoView, '#dashboard');
        },

        sync: function() {
            var thisView = this;
            this.$('.sync').addClass('loading');
            $.ajax({
                url: '/api/v1/user/sync',
                method: 'POST',
                dataType: 'json',
                success: function(user) {
                    sessionData = user;
                    thisView.sessionUser = new User.UserModel(sessionData);
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
        template: Templates.Dashboard.repoDetails(),
        events: {
            'click .enable': 'toggleRepo',
        },

        render: function() {
            this.$el.html(this.template({repo: this.model.toJSON()}));
            return this;
        },

        toggleRepo: function() {
            var thisView = this;
            var enabled = !this.model.get('enabled');
            this.model.set('enabled', enabled);
            this.render();
            this.model.save(null, {
                error: function() {
                    thisView.render();
                }
            });
        },

        toggleEnabledButton: function(enabled) {
            var $toggle = this.$('.enable');
            if (enabled) {
                $toggle.addClass('active');
                $toggle.html('Enabled');
            } else {
                $toggle.removeClass('active');
                $toggle.html('Disabled');
            }
        },

    });

    return Dashboard;
});
