<h2 class="ui header">
  {{ repo.name }}
  {{#if repo.description}}
  <div class="sub header">{{ repo.description }}</div>
  {{/if}}
</h2>
<p>Enabled: {{#if repo.enabled}}yes{{else}}no{{/if}}</p>
