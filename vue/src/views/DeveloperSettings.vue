<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="display-1">
					{{ $t( 'developersettings' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'developersettings-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-tabs
					v-model="tabs"
				>
					<v-tab>{{ $t( 'registerapps' ) }}</v-tab>
					<v-tab>{{ $t( 'clientapps' ) }}</v-tab>
					<v-tab>{{ $t( 'authorizedapps' ) }}</v-tab>
				</v-tabs>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-tabs-items v-model="tabs">
					<v-tab-item>
						<v-row>
							<v-col cols="12">
								<v-text-field
									ref="appName"
									v-model="appName"
									:label="$t( 'appname' )"
									prepend-icon="mdi-pencil-outline"
									required
									:rules="appNameRules"
								/>
							</v-col>

							<v-col cols="12">
								<v-text-field
									ref="redirectUrl"
									v-model="redirectUrl"
									:label="$t( 'authcallbackurl' )"
									prepend-icon="mdi-link-variant"
									required
									:rules="redirectUrlRules"
								/>
							</v-col>

							<v-col cols="12" lg="8">
								<v-btn
									color="primary"
									class="pa-4"
									@click="registerApp( appName, redirectUrl )"
								>
									{{ $t( 'registeroauthapp' ) }}
								</v-btn>
							</v-col>
						</v-row>

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
													'id', clientAppCreated.client_id )"
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
													'secret', clientAppCreated.client_secret )"
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
					</v-tab-item>

					<v-tab-item>
						<v-row v-if="numClientApps === 0">
							<v-col cols="12">
								<p class="title text--secondary">
									{{ $t( 'developersettings-noclientappsfoundtext' ) }}
								</p>
							</v-col>
						</v-row>

						<v-row v-for="app in clientApps"
							:key="app.client_id"
							class="elevation-2 ma-1 mb-4"
						>
							<v-col cols="12">
								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'appname' ) }}</dt>
									<dd>{{ app.name }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'clientid' ) }}</dt>
									<dd class="app-client-id">{{ app.client_id }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'createdby' ) }}</dt>
									<dd>{{ app.user.username }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<template
										v-if="$store.state.user.user.username === app.user.username"
									>
										<dt class="me-2 mt-5 font-weight-bold">
											{{ $t( 'redirecturl' ) }}
										</dt>

										<dd>
											<v-text-field
												:ref="`url-${app.client_id}`"
												:value="app.redirect_url"
												required
												:rules="redirectUrlRules"
												@change="val => newRedirectUrl = val"
											/>
										</dd>

										<dd :ref="`app-${app.client_id}`" />
									</template>

									<template
										v-else
									>
										<dt class="me-2 font-weight-bold">
											{{ $t( 'redirecturl' ) }}
										</dt>
										<dd>{{ app.redirect_url }}</dd>
									</template>
								</dl>
							</v-col>

							<v-col v-if="$store.state.user.user.username === app.user.username"
								cols="12"
							>
								<v-btn
									color="primary"
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
									color="error"
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
						<v-row>
							<v-col cols="12">
								<v-pagination
									v-if="numClientApps > 0"
									v-model="clientAppsPage"
									:length="Math.ceil( numClientApps / itemsPerPage )"
									class="ma-4"
									total-visible="5"
									@input="goToClientAppsPage"
								/>
							</v-col>
						</v-row>
					</v-tab-item>

					<v-tab-item>
						<v-row v-if="numAuthorizedApps === 0">
							<v-col cols="12">
								<p class="title text--secondary">
									{{ $t( 'developersettings-noauthorizedappsfoundtext' ) }}
								</p>
							</v-col>
						</v-row>

						<v-row v-for="app in authorizedApps"
							:key="app.id"
							class="elevation-2 ma-1 mb-4"
						>
							<v-col cols="12">
								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'appname' ) }}</dt>
									<dd>{{ app.application.name }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'clientid' ) }}</dt>
									<dd>{{ app.application.client_id }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'createdby' ) }}</dt>
									<dd>{{ app.application.user.username }}</dd>
								</dl>

								<dl
									class="row ma-1 pa-1"
								>
									<dt class="me-2 font-weight-bold">{{ $t( 'redirecturl' ) }}</dt>
									<dd>{{ app.application.redirect_url }}</dd>
								</dl>
							</v-col>

							<v-col cols="12">
								<v-btn
									color="error"
									@click="deleteAuthorizedApp( app.id )"
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

						<v-row>
							<v-col cols="12">
								<v-pagination
									v-if="numAuthorizedApps > 0"
									v-model="authorizedAppsPage"
									:length="Math.ceil( numAuthorizedApps / itemsPerPage )"
									class="ma-4"
									total-visible="5"
									@input="goToAuthorizedAppsPage"
								/>
							</v-col>
						</v-row>
					</v-tab-item>
				</v-tabs-items>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import urlRegex from '@/plugins/url-regex';

export default {
	data() {
		return {
			tabs: null,
			appName: '',
			redirectUrl: '',
			clientAppsPage: 1,
			authorizedAppsPage: 1,
			itemsPerPage: 10,
			newRedirectUrl: '',
			isAppCreated: false,
			redirectUrlRules: [
				( v ) => !!v || this.$t( 'urlrequired' ),
				( v ) => urlRegex.test( v ) || this.$t( 'urlinvalid' ),
				( v ) => ( v || '' ).length <= 255 || this.$t( 'urlcharslimit' )
			],
			appNameRules: [
				( v ) => !!v || this.$t( 'appnamerequired' ),
				( v ) => ( v || '' ).length <= 255 || this.$t( 'appnamecharslimit' )
			]
		};
	},
	computed: {
		...mapState( 'user', [
			'user',
			'clientApps',
			'numClientApps',
			'authorizedApps',
			'numAuthorizedApps',
			'clientAppCreated'
		] ),

		_clientAppUpdated() {
			return this.clientAppUpdated;
		},

		_clientAppCreated() {
			return this.clientAppCreated;
		}
	},
	methods: {
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
		registerApp( appName, redirectUrl ) {
			const refs = this.$refs;

			if ( !refs.appName.validate() ) {
				refs.appName.validate( true );
				return;
			}

			if ( !refs.redirectUrl.validate() ) {
				refs.redirectUrl.validate( true );
				return;
			}

			this.$store.dispatch( 'user/registerApp', { name: appName, url: redirectUrl } );
		},
		listClientApps() {
			this.$store.dispatch( 'user/listClientApps', this.clientAppsPage );
		},
		updateClientApp( app ) {
			const appUrl = this.$refs[ 'url-' + app.client_id ][ 0 ];

			if ( !this.newRedirectUrl || !appUrl.validate() ) {
				return;
			}

			this.$store.dispatch( 'user/updateClientApp', {
				clientId: app.client_id,
				redirectUrl: this.newRedirectUrl
			} );
		},
		deleteClientApp( clientId ) {
			this.$store.dispatch( 'user/deleteClientApp', clientId );
		},
		listAuthorizedApps() {
			this.$store.dispatch( 'user/listAuthorizedApps', this.authorizedAppsPage );
		},
		deleteAuthorizedApp( id ) {
			this.$store.dispatch( 'user/deleteAuthorizedApp', id );
		},
		goToClientAppsPage( num ) {
			this.clientAppsPage = num;
			this.listClientApps();
		},
		goToAuthorizedAppsPage( num ) {
			this.authorizedAppsPage = num;
			this.listAuthorizedApps();
		},
		closeAppDetailsAlert() {
			this.isAppCreated = false;
		}
	},
	watch: {
		_clientAppCreated() {
			this.isAppCreated = true;
			this.$refs.appName.reset();
			this.$refs.redirectUrl.reset();
		}
	},
	mounted() {
		this.listClientApps();
		this.listAuthorizedApps();
	}
};
</script>
