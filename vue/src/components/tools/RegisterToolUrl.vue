<template>
	<v-container>
		<v-row>
			<v-col
				lg="10"
				cols="8"
			>
				<v-text-field
					ref="url"
					v-model="fileUrl"
					prepend-icon="mdi-link-variant"
					:rules="validationRules"
					required
					:disabled="!$can( 'add', 'crawler/url' )"
				>
					<template #label>
						<InputLabel :label="$t( 'jsonfileurl' )" required />
					</template>
				</v-text-field>
			</v-col>
			<v-col
				lg="2"
				cols="4"
			>
				<v-btn
					class="mt-4"
					color="primary base100--text"
					width="100%"
					:disabled="!$can( 'add', 'crawler/url' )"
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
				<v-row v-if="$can( 'add', 'crawler/url' )
					&& numUserCreatedUrls === 0"
				>
					<v-col cols="12">
						<p class="text-h6 text--secondary">
							{{ $t( 'nourlsfounderror' ) }}
						</p>
					</v-col>
				</v-row>

				<v-data-table
					v-if="numUserCreatedUrls > 0"
					:headers="headers"
					:items="userCreatedUrls"
					:options.sync="options"
					:server-items-length="numUserCreatedUrls"
					class="elevation-2"
					hide-default-footer
					mobile-breakpoint="0"
					:loading="urlsLoading"
				>
					<template #[`item.url`]="{ item }">
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
							v-if="$can( 'delete', item )"
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
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import InputLabel from '@/components/common/InputLabel';
import { isValidHttpUrl } from '@/helpers/validation';
import { filterEmpty } from '@/helpers/object';

export default {
	name: 'RegisterToolUrl',
	components: {
		InputLabel
	},
	data() {
		return {
			page: 1,
			itemsPerPage: 10,
			fileUrl: '',
			urlsLoading: null,
			filters: {
				ordering: null
			},
			options: {}
		};
	},
	computed: {
		...mapState( 'crawler', [ 'userCreatedUrls', 'numUserCreatedUrls' ] ),
		headers() {
			return [
				{
					text: this.$t( 'jsonfileurl' ),
					value: 'url',
					sortable: true
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
		},
		validationRules() {
			const urlRule = ( v ) => !v ? true : isValidHttpUrl( v ) || this.$t( 'urlinvalid' );
			const requiredRule = ( v ) => !!v || this.$t( 'required-field' );
			return [ urlRule, requiredRule ];
		}
	},
	methods: {
		registerUrl( url ) {
			if ( !this.fileUrl || !isValidHttpUrl( this.fileUrl ) ) {
				this.$refs.url.validate( true );
				return;
			}

			this.$store.dispatch( 'crawler/registerUrl', url );
			this.fileUrl = '';
			this.$refs.url.reset();
		},
		unregisterUrl( url ) {
			this.$store.dispatch( 'crawler/unregisterUrl', url );
		},
		goToNextPage( page ) {
			this.page = page;
			this.getUrlsCreatedByUser();
		},
		setRouteQueryParams() {
			this.$router.push( {
				name: 'addremovetools',
				query: {
					tab: 'urls',
					...filterEmpty( {
						page: this.page, ...this.filters } ) }
			} ).catch( () => {} );
		},
		getUrlsCreatedByUser() {
			this.urlsLoading = true;
			const res = this.$store.dispatch( 'crawler/getUrlsCreatedByUser',
				{ page: this.page, filters: this.filters } );
			if ( res === undefined ) { // TODO: force all actions that make api call to always
				this.setRouteQueryParams();// return a promise, so this if else block can be removed
				this.urlsLoading = false;
			} else {
				res.then( this.setRouteQueryParams )
					.finally( () => {
						this.urlsLoading = false;
					} );
			}
		},
		/**
		 * Allow deep linking to filtered results by reconstructing internal
		 * state based on data provided in the current query string.
		 *
		 * @return {boolean} True if state was updated. False otherwise.
		 */
		loadStateFromQueryString() {
			const params = new URLSearchParams(
				document.location.search.substring( 1 )
			);
			let gotQueryData = false;
			for ( const [ key, value ] of params ) {
				if ( value === undefined ) {
					continue;
				}
				switch ( key ) {
					case 'ordering':
						this.filters.ordering = value;

						if ( value[ 0 ] === '-' ) {
							this.options.sortBy = [ value.replace( '-', '' ) ];
							this.options.sortDesc = [ true ];
						} else {
							this.options.sortBy = [ value ];
							this.options.sortDesc = [ false ];
						}

						gotQueryData = true;
						break;
					case 'page':
						this.page = parseInt( value, 10 );
						gotQueryData = true;
						break;
					default:
						// ignore this param
						break;
				}
			}
			return gotQueryData;
		}
	},
	watch: {
		options: {
			handler( _, oldVal ) {
				const {
					sortBy,
					sortDesc
				} = this.options;
				if ( sortBy.length === 1 && sortDesc.length === 1 ) {
					if ( sortDesc[ 0 ] === false ) {
						this.filters.ordering = sortBy[ 0 ];
					} else {
						this.filters.ordering = `-${sortBy[ 0 ]}`;
					}
					this.getUrlsCreatedByUser();
				} else if ( oldVal.sortBy ) {
					this.filters.ordering = null;
					this.getUrlsCreatedByUser();
				}
			},
			deep: true
		}
	},
	mounted() {
		this.loadStateFromQueryString();
		this.$store.dispatch( 'user/getUserInfo', { vm: this } ).then(
			( user ) => {
				if ( user.is_authenticated ) {
					this.getUrlsCreatedByUser();
				}
			}
		);
	}
};
</script>
