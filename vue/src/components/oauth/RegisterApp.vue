<template>
	<v-container v-if="schema">
		<v-row v-if="isAppCreated">
			<v-col
				cols="12"
			>
				<v-alert text
					color="secondary"
					dismissible
					@input="closeAppDetailsAlert"
				>
					<v-row>
						<v-col lg="2"
							cols="3"
							class="py-1 mt-1 font-weight-bold"
						>
							{{ $t( 'clientid' ) }}
						</v-col>

						<v-col lg="6"
							cols="5"
							class="py-1 mt-1 app-client-id"
						>
							{{ clientAppCreated.client_id }}
						</v-col>

						<v-col lg="2"
							cols="2"
							class="py-1"
						>
							<v-btn class="text-none"
								icon
								tile
								:aria-label="$t( 'clicktocopy' )"
								@click="copyToClipboard(
									'id',
									clientAppCreated.client_id
								)"
							>
								<v-icon
									plain
								>
									mdi-content-copy
								</v-icon>
							</v-btn>
						</v-col>

						<v-col lg="2"
							cols="2"
							class="py-1"
						>
							<p ref="app-id-clipboard" class="font-weight-bold" />
						</v-col>
					</v-row>

					<v-row class="py-0">
						<v-col lg="2"
							cols="3"
							class="py-1 mt-1 font-weight-bold"
						>
							{{ $t( 'clientsecret' ) }}
						</v-col>

						<v-col lg="6"
							cols="5"
							class="py-1 mt-1 app-client-secret"
						>
							{{ clientAppCreated.client_secret }}
						</v-col>

						<v-col lg="2"
							cols="2"
							class="py-1"
						>
							<v-btn class="text-none"
								icon
								tile
								:aria-label="$t( 'clicktocopy' )"
								@click="copyToClipboard(
									'secret',
									clientAppCreated.client_secret
								)"
							>
								<v-icon
									plain
								>
									mdi-content-copy
								</v-icon>
							</v-btn>
						</v-col>

						<v-col lg="2"
							cols="2"
							class="py-1"
						>
							<p ref="app-secret-clipboard"
								class="font-weight-bold"
							/>
						</v-col>
					</v-row>
				</v-alert>
			</v-col>
		</v-row>
		<v-row v-else>
			<v-form
				ref="form"
				v-model="valid"
				class="flex"
			>
				<v-row dense class="my-4">
					<v-col
						cols="12"
						class="pe-4"
					>
						<v-row>
							<v-col
								v-for="( uischema, id ) in layout"
								:key="id"
								cols="12"
							>
								<InputWidget
									v-model="appinfo[ id ]"
									:schema="schema.properties[ id ]"
									:ui-schema="uischema"
								/>
							</v-col>
						</v-row>
					</v-col>
				</v-row>
			</v-form>
			<v-col cols="12" lg="8">
				<v-btn
					color="primary base100--text"
					class="pa-4"
					:disabled="!valid || !$can( 'add', 'oauth2_provider/application' )"
					@click="registerApp"
				>
					{{ $t( 'registeroauthapp' ) }}
				</v-btn>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import InputWidget from '@/components/common/InputWidget';

export default {
	name: 'RegisterApp',
	components: {
		InputWidget
	},
	data() {
		return {
			valid: false,
			appinfo: {
				name: null,
				redirect_url: null
			},
			layout: {
				name: {
					icon: 'mdi-pencil-outline',
					label: this.$t( 'appname' ),
					required: true
				},
				redirect_url: {
					icon: 'mdi-link-variant',
					label: this.$t( 'authcallbackurl' ),
					required: true
				}
			},
			isAppCreated: false
		};
	},
	computed: {
		...mapState( 'oauth', [ 'clientAppCreated' ] )
	},
	asyncComputed: {
		schema: {
			get() {
				return this.getRequestSchema( 'oauth_applications_create' );
			},
			default: false
		}
	},
	methods: {
		...mapActions( 'api', [ 'getRequestSchema' ] ),

		copyToClipboard( item, value ) {
			const refs = this.$refs,
				appClipboard = item === 'id' ? 'app-id-clipboard' : 'app-secret-clipboard',
				message = this.$t( 'copiedtoclipboard' );

			this.$copyText( value ).then( function () {
				refs[ appClipboard ].innerText = message;
				setTimeout( function () {
					refs[ appClipboard ].innerText = '';
				}, 20000 );
			} );
		},
		registerApp() {
			const newapp = { ...this.appinfo };
			this.$store.dispatch( 'oauth/registerApp', newapp ).then(
				() => {
					if ( this.clientAppCreated ) {
						this.isAppCreated = true;
						this.$refs.form.reset();
					}
				}
			);
		},
		closeAppDetailsAlert() {
			this.isAppCreated = false;
		}
	}
};
</script>
