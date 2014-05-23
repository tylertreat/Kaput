/** @jsx React.DOM */

define([
    'jquery',
    'semantic',
    'react',
    'backbone',
    'moment',
    'pace',
    'models/Repository',
    'models/User',
    'jsx!components/Navigation',
], function($, Semantic, React, Backbone, Moment, Pace, Repository, User, Navigation) {

    var Dashboard = React.createClass({

        componentDidMount: function() {
            Pace.start({ajax: {trackMethods: ['GET', 'POST']}});
            if (this.props.user.repos.length === 0) {
                this.props.sync();
                return;
            }
            
            if (!this.props.user.active_repo) {
                this.props.user.active_repo = this.props.user.repos[0];
            }

            $(this.getDOMNode()).find('.repo-select')
                .val(this.props.user.active_repo.id);
        },

        render: function() {
            var lastSynced = this.props.user.last_synced;
            if (!lastSynced) {
                lastSynced = 'never';
            } else {
                lastSynced = Moment.unix(lastSynced).fromNow();
            }

            var activeRepo = _.findWhere(
                this.props.user.repos, {id: this.props.user.active_repo});

            return (
                <div>
                    <Navigation user={this.props.user} changeRepo={this.props.changeRepo} /> 
                    <div id="dashboard-container" className="ui segment">
                        <div className="ui ribbon label">Last synced {lastSynced}</div>
                        <div className="ui right floated button sync" onClick={this.sync}>
                            <i className="github alternate icon"></i> Sync
                        </div>
                        <Repo repo={activeRepo} />
                    </div>
                </div>
            );
        },

        sync: function() {
            this.props.sync();
        },

        changeActiveRepo: function(e) {
            this.props.changeActiveRepo(e.target.value);
        },

    });

    var Repo = React.createClass({
        
        render: function() {
            if (!this.props.repo) {
                return <div />;
            }

            var cx = React.addons.classSet;
            var btnClasses = cx({
                'ui': true,
                'toggle': true,
                'button': true,
                'enable': true,
                'active': this.props.repo.enabled,
            });

            var description;
            if (this.props.repo.description) {
                description = (
                    <div className="sub header">
                        {this.props.repo.description}
                    </div>
                );
            }

            return (
                <div>
                    <div className="title">
                        <div className="pull-left" style={{marginRight: 15, marginTop: 10}}>
                            <div className={btnClasses} onClick={this._toggle}>
                                {this.props.repo.selected ? 'Enabled' : 'Enable'}
                            </div>
                        </div>
                        <h2 className="ui header">
                            {this.props.repo.name}
                            {description}
                        </h2>
                    </div>
                    <p>Enabled: {this.props.repo.enabled ? 'Yes' : 'No'}</p>
                </div>
            );
        },

        _toggle: function() {
            var enabled = !this.props.repo.enabled;
            this.props.repo.enabled = enabled;
            this.forceUpdate();
            new Repository.RepoModel(this.props.repo).save(null, {
                error: function() {
                    this.props.repo.enabled = !enabled;
                    this.forceUpdate();
                }.bind(this)
            });
        },

    });

    return Dashboard;
});

