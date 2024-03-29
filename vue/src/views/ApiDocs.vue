<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'apidocs' ) }}
				</h2>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<rapi-doc
					v-if="apispec"
					ref="rapidoc"
					class="no-gutters flex-wrap flex-column fill-height elevation-1 py-6"
					allow-api-list-style-selection="false"
					allow-authentication="false"
					allow-search="false"
					allow-server-selection="false"
					allow-spec-file-load="false"
					allow-spec-url-load="false"
					layout="column"
					load-fonts="false"
					:primary-color="$vuetify.theme.themes.light.primary"
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
import fetchMetaInfo from '@/helpers/metadata';

export default {
	name: 'ApiDocs',
	metaInfo() {
		return fetchMetaInfo( 'apidocs' );
	},
	computed: {
		...mapState( 'api', [ 'apispec' ] ),
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
		this.fetchOpenAPISchema().then( () => this.loadSpec( this.apispec ) );
	}
};
</script>
