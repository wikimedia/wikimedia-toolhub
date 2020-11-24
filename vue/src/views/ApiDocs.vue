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
		api-key-name="X-CSRFToken"
		api-key-location="header"
		:api-key-value="user.csrf_token"
	/>
</template>

<script>
import { mapState } from 'vuex';
import 'rapidoc';

export default {
	name: 'ApiDocs',
	computed: {
		...mapState( 'user', [ 'user' ] )
	}
};
</script>

<style>
#apidoc {
	/* stylelint-disable-next-line plugin/no-unsupported-browser-features -- vh */
	height: 100vh;
	width: 100%;
}
</style>
