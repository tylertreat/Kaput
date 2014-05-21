/** @jsx React.DOM */

define([
    'jquery',
    'semantic',
    'react',
    'backbone',
    'ReactChosen',
], function($, Semantic, React, Backbone, Chosen) {

    var Navigation = React.createClass({

        render: function() {
            return (
                <div>
                    <div className="ui menu large">
                        <div className="item" style={{fontWeight: 'bold'}}>
                            Kaput.io
                        </div>
                        <div className="item">
                        <Chosen
                            defaultValue={this.props.user.active_repo}
                            noResultsText="No repos match"
                            placeholderTextSingle="Select a repo"
                            width="202px"
                            onChange={this.changeActiveRepo}>
                            {
                                this.props.user.repos.map(function(repo) {
                                    return (
                                        <option key={repo.id} value={repo.id}>
                                            {repo.name}
                                        </option>
                                    );
                                })
                            }
                        </Chosen>
                        </div>
                        <div className="right menu">
                            <div className="ui dropdown item">
                                {this.props.user.username} 
                                <i className="icon dropdown"></i>
                                <div className="menu">
                                    <a className="item" href="/logout">
                                        <i className="sign out icon"></i> Sign Out
                                    </a>
                                    <a className="item" href="/#/account">
                                        <i className="settings icon"></i> Account Settings
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        },

        changeActiveRepo: function(e) {
            this.props.changeRepo(e.target.value);
        },

    });

    return Navigation;
});
