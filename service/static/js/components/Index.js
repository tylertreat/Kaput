/** @jsx React.DOM */

define([
    'react',
], function(React) {

    var Index = React.createClass({

        render: function() {
            return (
                <div>
                    <div className="header segment">
                        <div className="ui page two column grid">
                            <div className="column">
                                <h1 className="ui header">Kaput.io</h1>
                            </div>
                            <div className="column">
                                <a href="/login" className="ui button green pull-right">
                                    <i className="icon user"></i> Sign in
                                </a>
                            </div>
                        </div>
                    </div>

                    <div className="masthead segment banner">
                      <div className="ui page two column grid">
                        <div className="column">
                            <h1 className="ui header">
                                <span className="green">$#@% happens.</span> 
                                Know when, where, and why.
                            </h1>
                            <h2 className="ui header">
                                <span className="green">Intelligent issue awareness</span> 
                                lets your teams respond to problems as they arise, in real-time.
                            </h2>
                            <a href="/login" className="ui large green icon button">
                                <i className="github alternate icon"></i>
                                Sign in with GitHub
                            </a>
                        </div>
                        <div className="column">
                            <img className="pull-right" src="static/images/diagram.png"
                                width="550" />
                        </div>
                      </div>
                    </div>
                </div>
            );
        },

    });

    return Index;
});

