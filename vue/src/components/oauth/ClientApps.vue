<template>
	<v-container v-if="schema">
		<v-row v-if="loaded && numClientApps === 0">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'developersettings-noclientappsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row v-for="app in clientApps"
			:key="app.client_id"
			class="elevation-2 ma-1 mb-4"
		>
			<v-col cols="12">
				<dl class="row ma-1 pa-1">
					<dt class="me-2 font-weight-bold">{{ $t( 'appname' ) }}</dt>
					<dd>{{ app.name }}</dd>
				</dl>
				<dl class="row ma-1 pa-1">
					<dt class="me-2 font-weight-bold">{{ $t( 'clientid' ) }}</dt>
					<dd class="app-client-id">{{ app.client_id }}</dd>
				</dl>
				<dl class="row ma-1 pa-1">
					<dt class="me-2 font-weight-bold">{{ $t( 'createdby' ) }}</dt>
					<dd>{{ app.user.username }}</dd>
				</dl>
				<dl class="row ma-1 pa-1">
					<template v-if="$can( 'change', app )">
						<dt class="me-2 mt-5 font-weight-bold">
							{{ $t( 'redirecturl' ) }}
						</dt>
						<dd class="flex">
							<InputWidget
								v-model="redirectUrls[ app.client_id ]"
								:schema="schema.properties.redirect_url"
								:ui-schema="layout.redirect_url"
							/>
						</dd>
					</template>
					<template v-else>
						<dt class="me-2 font-weight-bold">
							{{ $t( 'redirecturl' ) }}
						</dt>
						<dd>{{ app.redirect_url }}</dd>
					</template>
				</dl>
			</v-col>
			<v-col v-if="$can( 'change', app )"
				cols="12"
			>
				<v-btn
					color="primary base100--text"
					class="me-2"
					@click="updateClientApp( app )"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-pencil
					</v-icon>

					{{ $t( 'update' ) }}
				</v-btn>

				<v-btn
					color="error base100--text"
					@click="deleteClientApp( app.client_id )"
				>
					<v-icon
						dark
						class="me-2"
					>
						mdi-delete
					</v-icon>
					{{ $t( 'delete' ) }}
				</v-btn>
			</v-col>
		</v-row>
		<v-row v-if="pages > 1">
			<v-col cols="12">
				<v-pagination
					v-model="page"
					:length="pages"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import InputWidget from '@/components/common/InputWidget';

export default {
	name: 'ClientApps',
	components: {
		InputWidget
	},
	data() {
		return {
			loaded: false,
			page: 1,
			itemsPerPage: 10,
			redirectUrls: {},
			layout: {
				redirect_url: {
					icon: '',
					label: '',
					required: true
				}
			}
		};
	},
	computed: {
		...mapState( 'oauth', [ 'clientApps', 'numClientApps' ] ),
		pages() {
			return Math.ceil( this.numClientApps / this.itemsPerPage );
		}
	},
	asyncComputed: {
		schema: {
			get() {
				return this.getRequestSchema(
					'oauth_applications_partial_update'
				);
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),

		listClientApps() {
			this.$store.dispatch( 'oauth/listClientApps', this.page ).then(
				() => {
					this.loaded = true;
				}
			);
		},
		updateClientApp( app ) {
			this.$store.dispatch( 'oauth/updateClientApp', {
				clientId: app.client_id,
				redirectUrl: this.redirectUrls[ app.client_id ]
			} );
		},
		deleteClientApp( clientId ) {
			this.$store.dispatch( 'oauth/deleteClientApp', clientId );
		},
		goToPage( num ) {
			this.page = num;
			this.listClientApps();
		}
	},
	watch: {
		clientApps: {
			handler( newVal ) {
				this.redirectUrls = {};
				newVal.forEach( ( app ) => {
					this.redirectUrls[ app.client_id ] = app.redirect_url;
				} );
			},
			immediate: true
		}
	},
	mounted() {
		this.listClientApps();
	}
};
</script>
