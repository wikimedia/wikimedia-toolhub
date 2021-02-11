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
					<v-col
						lg="10"
						cols="8"
					>
						<v-text-field
							ref="url"
							v-model="fileUrl"
							:label="$t( 'jsonfileurl' )"
							prepend-icon="mdi-link-variant"
							:rules="requiredRule.concat( urlRule )"
							required
							:disabled="$store.state.user.user.is_authenticated
								=== false"
						/>
					</v-col>
					<v-col
						lg="2"
						cols="4"
					>
						<v-btn
							class="mt-4"
							color="primary"
							width="100%"
							:disabled="$store.state.user.user.is_authenticated
								=== false"
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
					<v-col cols="12">
						<v-row v-if="$store.state.user.user.is_authenticated
							=== true && numUserCreatedUrls === 0"
						>
							<v-col cols="12">
								<p class="title text--secondary">
									{{ $t( 'nourlsfounderror' ) }}
								</p>
							</v-col>
						</v-row>

						<v-data-table
							v-if="numUserCreatedUrls > 0"
							:headers="headers"
							:page="page"
							:items-per-page="itemsPerPage"
							:items="userCreatedUrls"
							class="elevation-2"
							hide-default-footer
							mobile-breakpoint="0"
							:custom-sort="customSortUrls"
						>
							<template #[`item.json_file_url`]="{ item }">
								<a
									:href="item.url"
									target="_blank"
								>{{ item.url }}</a>
							</template>
							<template #[`item.created_date`]="{ item }">
								{{ item.created_date | moment( 'lll' ) }}
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
							total-visible="5"
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
					<v-col
						cols="12"
					>
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
								>{{ $t( 'schemalink' ) }}</a>
							</p>
						</v-alert>
					</v-col>
				</v-row>
			</v-col> <!--end how this page works section-->
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import customSort from '@/plugins/sort.js';
import urlRegex from '@/plugins/url-regex';

export default {
	name: 'RegisterToolUrl',
	data() {
		return {
			page: 1,
			itemsPerPage: 10,
			fileUrl: '',
			urlRule: [ ( v ) => !v ? true : urlRegex.test( v ) || this.$t( 'urlinvalid' ) ],
			requiredRule: [ ( v ) => !!v || 'This field is required' ]
		};
	},
	computed: {
		...mapState( 'user', [
			'userCreatedUrls',
			'numUserCreatedUrls'
		] ),

		isUserAuthenticated() {
			return this.$store.state.user.user.is_authenticated;
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
			if ( !this.fileUrl || !urlRegex.test( this.fileUrl ) ) {
				this.$refs.url.validate( true );
				return;
			}

			this.$store.dispatch( 'user/registerUrl', url );
			this.fileUrl = '';
			this.$refs.url.reset();
		},
		unregisterUrl( urlObj ) {
			this.$store.dispatch( 'user/unregisterUrl', urlObj );
		},
		goToNextPage( page ) {
			this.page = page;
			this.getUrlsCreatedByUser();
		},
		getUrlsCreatedByUser() {
			this.$store.dispatch( 'user/getUrlsCreatedByUser', this.page );
		},
		customSortUrls( items, index, isDesc ) {
			return customSort( items, index, isDesc );
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
