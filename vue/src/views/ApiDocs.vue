<template>
	<rapi-doc
		id="apidoc"
		spec-url="/api/.schema"
		class="no-gutters flex-wrap flex-column fill-height"
		allow-api-list-style-selection="false"
		allow-authentication="false"
		allow-search="false"
		allow-server-selection="false"
		allow-spec-file-load="false"
		allow-spec-url-load="false"
		render-style="view"
		schema-description-expanded="false"
		schema-style="tree"
		show-components="true"
		show-header="false"
		theme="light"
		use-path-in-nav-bar="true"
	/>
</template>

<script>
import 'rapidoc';

export default {
	name: 'ApiDocs'
};
</script>

<style>
#apidoc {
  height:100vh;
  width:100%;
}
</style>
