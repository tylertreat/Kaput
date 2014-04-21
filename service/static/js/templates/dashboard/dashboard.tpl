<div>
    <div class="ui menu large">
        <div class="item" style="font-weight:bold">Kaput.io</div>
        <a class="active item"><i class="code icon"></i> Repos</a>
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

<div id="dashboard">
    <div class="ui two column grid">
        <div id="repos" class="column"></div>
        <div id="repo-details" class="column"></div>
    </div>
</div>
