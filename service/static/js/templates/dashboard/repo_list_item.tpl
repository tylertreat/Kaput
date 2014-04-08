<div class="item">
    {{#if repo.enabled}}
    <div class="ui toggle button active enable">Enabled</div>
    {{else}}
    <div class="ui toggle button enable">Enable</div>
    {{/if}}
    <div class="content">
        <div class="header">{{ repo.name }}</div> {{ repo.description }}
    </div>
</div>
