/** @jsx React.DOM */

define([
    'jquery',
    'semantic',
    'react',
    'backbone',
    'components/Index',
    'components/Dashboard',
    'components/Account',
    'models/User',
], function($, Semantic, React, Backbone, Index, Dashboard, Account, User) {

    var AppRouter = Backbone.Router.extend({
        routes: {
            '': 'index',
            'account': 'account',
        },

        index: function() {
            this._replaceView('index');
        },

        account: function() {
            this._replaceView('account');
        },

        _replaceView: function(view) {
            React.renderComponent(
                <RootComponent
                    isAuthenticated={sessionData && sessionData.is_authenticated}
                    router={this}
                    view={view} />, $('#container')[0]
            );
        },

    });

    var RootComponent = React.createClass({
        getInitialState: function() {
            return {user: sessionData};
        },

        render: function() {
            var view;
            if (this.props.isAuthenticated) {
                if (this.props.view === 'index') {
                    view = (
                        <Dashboard
                            user={this.state.user}
                            router={this.props.router}
                            sync={this.sync}
                            changeRepo={this.changeActiveRepo} />
                    );
                } else if (this.props.view === 'account') {
                    view = (
                        <Account
                            user={this.state.user}
                            router={this.props.router}
                            changeRepo={this.changeActiveRepo} />
                    );
                }
            } else {
                view = <Index />;
            }

            return view;
        },

        sync: function() {
            $('.sync').addClass('loading');
            $.ajax({
                url: '/api/v1/user/sync',
                method: 'POST',
                dataType: 'json',
                success: function(user) {
                    sessionData = user;
                    this.setState({user: sessionData});
                }.bind(this),
                complete: function() {
                    $('.sync').removeClass('loading');
                },
            });
        },

        changeActiveRepo: function(repoId) {
            var user = this.state.user;
            user.active_repo = repoId;
            new User.UserModel(user).save();
            this.setState({user: user});
        },
    });

    var initialize = function() {
        var appRouter = new AppRouter;
        Backbone.history.start();
    };

    return {
        initialize: initialize
    };
});

