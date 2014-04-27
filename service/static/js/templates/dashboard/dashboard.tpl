<div>
    <div class="ui menu large">
        <div class="item" style="font-weight:bold">Kaput.io</div>
        <select class="item repo-select">
            {{#each repos}}
            <option value="{{ this.id }}">{{ this.name }}</option>
            {{/each}}
        </select>
        <div class="right menu">
            <div class="ui dropdown item">
                {{ user.username }} <i class="icon dropdown"></i>
                <div class="menu">
                    <a class="item" href="/logout"><i class="sign out icon">
                        </i> Sign Out
                    </a>
                    <a class="item"><i class="settings icon"></i> Account Settings</a>
                </div>
            </div>
        </div>
    </div>
</div>

<div id="dashboard-container" class="ui segment">
    <div class="ui ribbon label">Last synced {{ lastSynced }}</div>
    <div class="ui right floated button sync">
        <i class="github alternate icon"></i> Sync
    </div>
    <div id="dashboard"></div>
</div>
