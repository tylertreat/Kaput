<div class="title">
    <div class="pull-left" style="margin-right:15px;margin-top:10px">
        {{#if repo.enabled}}
        <div class="ui toggle button active enable">Enabled</div>
        {{else}}
        <div class="ui toggle button enable">Disabled</div>
        {{/if}}
    </div>
    <h2 class="ui header">
    {{ repo.name }}
    {{#if repo.description}}
    <div class="sub header">{{ repo.description }}</div>
    {{/if}}
    </h2>
</div>
<p>Enabled: {{#if repo.enabled}}yes{{else}}no{{/if}}</p>
