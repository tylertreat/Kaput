define([
  'jquery',
  'underscore',
  'backbone',
  'pace',
  'moment',
  'templates',
  'BaseView',
  'Repository',
  'User',
], function($, _, Backbone, Pace, Moment, Templates, BaseView, Repository, User) {
    "use strict";

    var Account = {};

    Account.AccountSettingsView = BaseView.extend({
        template: Templates.Dashboard.accountSettings(),

        render: function() {
            this.$el.html(this.template({user: this.model.toJSON()}));
            this.$('.ui.dropdown').dropdown();
            this.enableValidation();
            return this;
        },

        enableValidation: function() {
            var thisView = this;

            var validation = {
                email: {
                  identifier  : 'primary-email',
                  rules: [
                    {
                      type: 'email',
                      prompt: 'Please enter your email address'
                    }
                  ]
                }
            };

            this.$('#settings-form').form(validation, {
                onSuccess: function() { thisView.saveSettings(); }
            });
        },

        saveSettings: function() {
            var thisView = this;
            var email = this.$('#primary-email').dropdown('get text');
            this.model.save({primary_email: email}, {
                success: function() {
                    thisView.$('.save').html('<i class="checkmark icon"></i> Saved');
                },
                error: function() {
                    thisView.$('.save').html('Save');
                }
            });
        },

        getFieldValue: function(fieldId) { 
            return $('#settings-form').form('get field', fieldId).val();
        },

    });

    return Account;
});
