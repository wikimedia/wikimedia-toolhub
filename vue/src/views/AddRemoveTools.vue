<template>
	<v-container>
		<v-row>
			<v-col
				md="8"
				cols="12"
				order-md="1"
				order="2"
			>
				<!--start add or remove tools section-->
				<v-row>
					<h2 class="display-1">
						{{ $t( 'addremovetools-pagetitle' ) }}
					</h2>
				</v-row>
				<v-row>
					<v-col
						lg="8"
						sm="10"
						cols="9"
						class="ps-0"
					>
						<v-text-field
							ref="url"
							v-model="fileUrl"
							:label="$t( 'jsonfileurl' )"
							prepend-icon="mdi-link-variant"
							:rules="urlRules"
							required
						/>
					</v-col>
					<v-col
						lg="2"
						sm="2"
						cols="3"
					>
						<v-btn
							class="mt-4"
							color="primary"
							dark
							width="100%"
							@click="registerUrl(fileUrl)"
						>
							{{ $t( 'add' ) }}
							<v-icon
								dark
								right
							>
								mdi-checkbox-marked-circle
							</v-icon>
						</v-btn>
					</v-col>
				</v-row>
				<v-row>
					<v-col
						lg="10"
						cols="12"
					>
						<v-alert
							v-if="apiErrorMsg"
							border="left"
							type="error"
							elevation="2"
							width="100%"
						>
							{{ $t( 'apierror' ) }} {{ apiErrorMsg }}
						</v-alert>

						<v-alert
							v-if="$store.state.user.is_authenticated === true &&
								numUserCreatedUrls === 0"
							border="left"
							type="info"
							elevation="2"
							color="primary"
							width="100%"
						>
							{{ $t( 'nourlsfounderror' ) }}
						</v-alert>

						<v-data-table
							v-if="numUserCreatedUrls > 0"
							:headers="headers"
							:page="page"
							:items-per-page="itemsPerPage"
							:items="userCreatedUrls"
							class="elevation-2"
							hide-default-footer
							mobile-breakpoint="0"
							:custom-sort="sortByLastModifiedDate"
						>
							<template #[`item.json_file_url`]="{ item }">
								<a
									:href="item.url"
									target="_blank"
								>{{ item.url }}</a>
							</template>
							<template #[`item.created_date`]="{ item }">
								{{ item.created_date | moment( "MMM DD, YYYY" ) }}
							</template>
							<template #[`item.btn_remove_url`]="{ item }">
								<v-btn
									class="mt-2 mb-2"
									color="error"
									dark
									@click="unregisterUrl(item)"
								>
									<v-icon
										dark
									>
										mdi-delete-circle
									</v-icon>
								</v-btn>
							</template>
						</v-data-table>

						<v-pagination
							v-if="numUserCreatedUrls > 0"
							v-model="page"
							:length="Math.ceil( numUserCreatedUrls / itemsPerPage )"
							class="ma-4"
							@input="goToNextPage"
						/>
					</v-col>
				</v-row>
			</v-col> <!--end add or remove tools section-->
			<v-col
				md="4"
				cols="12"
				order-md="2"
				order="1"
			>
				<!--start how this page works section-->
				<v-row>
					<v-alert
						color="primary"
						border="top"
						colored-border
						elevation="2"
					>
						<h3 class="headline">
							{{ $t( 'addremovetools-summarytitle' ) }}
						</h3>
						<v-divider class="pa-2" />
						<p>
							{{ $t( 'addremovetools-summary' ) }}
							<a
								href="https://meta.wikimedia.org/wiki/Toolhub/Data_model#Version_1.2.0"
								target="_blank"
							>{{ $t( 'schemalink' ) }}</a>.
						</p>
					</v-alert>
				</v-row>
				<v-row cols="12">
					<v-alert
						v-if="$store.state.user.is_authenticated === false"
						border="left"
						color="primary"
						dark
						elevation="2"
						type="info"
						width="100%"
					>
						{{ $t( 'addremovetools-nologintext' ) }}
					</v-alert>
				</v-row>
			</v-col> <!--end how this page works section-->
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';

export default {
	data() {
		return {
			fileUrl: '',
			urlRegex: new RegExp( '^(https?:\\/\\/)?((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' +
      '((\\d{1,3}\\.){3}\\d{1,3}))(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*(\\?[;:\\/&a-z\\d%_.~+=-]*)?' +
      '(\\#[-a-z\\d_]*)?$', 'i' ), // Taken from https://stackoverflow.com/a/5717133
			urlRules: [
				( v ) => !!v || this.$t( 'urlrequired' ),
				( v ) => this.urlRegex.test( v ) || this.$t( 'urlinvalid' )
			],
			page: 1,
			itemsPerPage: 10
		};
	},
	computed: {
		...mapState( [ 'userCreatedUrls', 'apiErrorMsg', 'numUserCreatedUrls' ] ),
		isUserAuthenticated() {
			return this.$store.state.user.is_authenticated;
		},
		headers() {
			return [
				{
					text: this.$t( 'jsonfileurl' ),
					value: 'json_file_url',
					sortable: false
				},
				{
					text: this.$t( 'datecreated' ),
					value: 'created_date',
					sortable: true
				},
				{
					text: this.$t( 'removeurl' ),
					value: 'btn_remove_url',
					sortable: false,
					align: 'right'
				}
			];
		}
	},
	methods: {
		registerUrl( url ) {
			if ( !this.fileUrl || !this.urlRegex.test( this.fileUrl ) ) {
				this.$refs.url.validate( true );
				return;
			}

			this.$store.dispatch( 'registerUrl', url );
			this.fileUrl = '';
			this.$refs.url.reset();
		},
		unregisterUrl( urlObj ) {
			this.$store.dispatch( 'unregisterUrl', urlObj );
		},
		goToNextPage( page ) {
			this.page = page;
			this.getUrlsCreatedByUser();
		},
		getUrlsCreatedByUser() {
			this.$store.dispatch( 'getUrlsCreatedByUser', this.page );
		},
		sortByLastModifiedDate( items, index, isDesc ) {
			items.sort( ( a, b ) => {
				if ( index[ 0 ] === 'created_date' ) {
					if ( !isDesc[ 0 ] ) {
						return new Date( b[ index ] ) - new Date( a[ index ] );
					} else {
						return new Date( a[ index ] ) - new Date( b[ index ] );
					}
				} else {
					if ( typeof a[ index ] !== 'undefined' ) {
						if ( !isDesc[ 0 ] ) {
							return a[ index ].toLowerCase().localeCompare( b[ index ]
								.toLowerCase() );
						} else {
							return b[ index ].toLowerCase().localeCompare( a[ index ]
								.toLowerCase() );
						}
					}
				}
				return 0;
			}
			);
			return items;
		}
	},
	watch: {
		isUserAuthenticated( value ) {
			if ( value ) {
				this.getUrlsCreatedByUser();
			}
		}
	},
	mounted() {
		this.getUrlsCreatedByUser();
	}
};
</script>
