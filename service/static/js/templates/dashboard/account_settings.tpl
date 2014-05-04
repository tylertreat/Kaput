<div>
    <div class="ui menu large">
        <div class="item" style="font-weight:bold"><a href="/">Kaput.io</a></div>
        <div class="right menu">
            <div class="ui dropdown item">
                {{ user.username }} <i class="icon dropdown"></i>
                <div class="menu">
                    <a class="item" href="/logout">
                        <i class="sign out icon"></i> Sign Out
                    </a>
                    <a class="item active" href="/#/account">
                        <i class="settings icon"></i> Account Settings
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="dashboard-container" class="ui segment">
    <h2 class="ui header">
      <i class="settings icon"></i>
      Account Settings
    </h2>

    <div id="settings-form" class="ui form">
      <div class="field">
        <label>Username</label>
        <div class="ui left labeled icon input">
          <input type="text" readonly="readonly" placeholder="Username"
              value="{{ user.username }}">
          <i class="user icon"></i>
        </div>
      </div>
      <div class="field">
        <label>Email</label>
        <div id="primary-email" class="ui selection dropdown">
          <div class="text">{{ user.primary_email }}</div>
          <i class="dropdown icon"></i>
          <div class="menu">
            {{#each user.emails}}
            <div class="item">{{ this }}</div>
            {{/each}}
          </div>
        </div> 
      </div>
      <div class="ui error message">
        <div class="header">We noticed some issues</div>
      </div>
      <div class="ui green submit button save">Save</div>
    </div>
</div>
