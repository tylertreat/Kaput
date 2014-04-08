define(function(require) {
    var Handlebars = require('handlebars');
    var _templates = {};

    _templates.Home = {
        index: require('text!templates/home/index.tpl'),
    };

    _templates.Dashboard = {
        dashboard: require('text!templates/dashboard/dashboard.tpl'),
        repos: require('text!templates/dashboard/repos.tpl'),
        repoListItem: require('text!templates/dashboard/repo_list_item.tpl'),
    };
 
    return {
        Home: {
            index: function() {
                return Handlebars.compile(_templates.Home.index);
            },
        },
        Dashboard: {
            dashboard: function() {
                return Handlebars.compile(_templates.Dashboard.dashboard);
            },
            repos: function() {
                return Handlebars.compile(_templates.Dashboard.repos);
            },
            repoListItem: function() {
                return Handlebars.compile(_templates.Dashboard.repoListItem);
            },
        }
    }
});

