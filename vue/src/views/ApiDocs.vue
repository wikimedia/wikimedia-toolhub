<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="display-1">
					{{ $t( 'apidocs' ) }}
				</h2>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<rapi-doc
					v-if="specLoaded"
					ref="rapidoc"
					class="no-gutters flex-wrap flex-column fill-height elevation-1 py-6"
					allow-api-list-style-selection="false"
					allow-authentication="false"
					allow-search="false"
					allow-server-selection="false"
					allow-spec-file-load="false"
					allow-spec-url-load="false"
					layout="column"
					render-style="view"
					schema-description-expanded="true"
					schema-style="tree"
					show-header="false"
					theme="light"
					use-path-in-nav-bar="true"
					api-key-name="X-CSRFToken"
					api-key-location="header"
					:api-key-value="user.csrf_token"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import 'rapidoc';

export default {
	name: 'ApiDocs',
	computed: {
		...mapState( 'api', [ 'apispec', 'specLoaded' ] ),
		...mapState( 'user', [ 'user' ] )
	},
	methods: {
		...mapActions( 'api', [ 'fetchOpenAPISchema' ] ),

		/**
		 * Load an OpenAPI spec into the display component.
		 *
		 * @param {Object|string} spec - OpenAPI spec or URL to fetch from
		 */
		loadSpec( spec ) {
			this.$nextTick( () => this.$refs.rapidoc.loadSpec( spec ) );
		}
	},
	watch: {
		apispec: {
			handler( newVal ) {
				if ( Object.keys( newVal ).length > 0 ) {
					this.loadSpec( newVal );
				}
			},
			deep: true
		}
	},
	mounted() {
		if ( this.specLoaded ) {
			this.loadSpec( this.apispec );
		} else {
			this.fetchOpenAPISchema();
		}
	}
};
</script>
