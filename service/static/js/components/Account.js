define([
    'jquery',
    'underscore',
    'backbone',
    'react',
    'models/Repository',
    'models/User',
    'jsx!components/Navigation',
], function($, _, Backbone, React, Repository, User, Navigation) {
    'use strict';

    var Account = React.createClass({

        render: function() {
            return (
                <div>
                    <Navigation user={this.props.user} changeRepo={this.props.changeRepo} />
                    <div id="dashboard-container" className="ui segment">
                        <h2 className="ui header">
                            <i className="settings icon pull-left"></i>
                            Account Settings
                        </h2>
                        <SettingsForm user={this.props.user} /> 
                    </div>  
                </div>
            );
        },

    });


    var SettingsForm = React.createClass({

        getInitialState: function() {
            return {saved: false};
        },

        render: function() {
            return (
                <div className="ui form">
                    <div className="field">
                        <label>Username</label>
                        <div className="ui left labeled icon input">
                            <input type="text" readOnly="readonly" placeholder="Username"
                                value={this.props.user.username} />
                            <i className="user icon"></i>
                        </div>
                    </div>
                    <div className="field">
                        <label>Email</label>
                        <div ref="primaryEmail" className="ui selection dropdown">
                            <div className="text">{this.props.user.primary_email }</div>
                            <i className="dropdown icon"></i>
                            <div className="menu">
                            {
                                this.props.user.emails.map(function(email) {
                                    return <div key={email} className="item">{email}</div>;
                                })
                            }
                            </div>
                        </div> 
                    </div>
                    <div className="ui error message">
                        <div className="header">We noticed some issues</div>
                    </div>
                    <div ref="save" className="ui green submit button">
                    {
                        (
                            this.state.saved ?
                                <span><i className="checkmark icon" /> Saved</span> :
                                <span>Save</span>
                        )
                    }
                    </div>
                </div>
            );
        },

        componentDidMount: function() {
            this._enableValidation();
            $(this.refs.primaryEmail.getDOMNode()).dropdown({
                onChange: function() {
                    this.setState({saved: false});
                }.bind(this),
            });
        },

        _enableValidation: function() {
            var validation = {
                email: {
                  identifier: 'primary-email',
                  rules: [
                    {
                      type: 'email',
                      prompt: 'Please enter your email address'
                    }
                  ]
                }
            };

            $(this.getDOMNode()).form(validation, {
                onSuccess: function() { this.saveSettings(); }.bind(this),
            });
        },

        saveSettings: function() {
            var email = $(this.refs.primaryEmail.getDOMNode()).dropdown('get text');
            this.props.user.primary_email = email;
            new User.UserModel(this.props.user).save(null, {
                success: function() {
                    this.setState({saved: true});
                }.bind(this),
            });
        },


    });

    return Account;
});
