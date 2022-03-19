<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'recentchanges' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'recentchanges-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-form ref="filtersform">
					<v-row>
						<v-col cols="6"
							lg="2"
							md="3"
						>
							<v-text-field
								v-model="filters.user"
								:label="$t( 'recentchanges-username' )"
								prepend-icon="mdi-account-outline"
							/>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
						>
							<v-select
								v-model="filters.target_type"
								:label="$t( 'recentchanges-type' )"
								:items="targetsComputed"
								item-value="type"
								item-text="label"
								prepend-icon="mdi-filter-variant"
							/>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
						>
							<v-menu
								:close-on-content-click="false"
								transition="scale-transition"
								offset-y
								left
							>
								<template #activator="{ on, attrs }">
									<v-text-field
										:value="formattedActions"
										:label="$t( 'recentchanges-action' )"
										readonly
										v-bind="attrs"
										prepend-icon="mdi-police-badge-outline"
										v-on="on"
									/>
								</template>
								<v-list>
									<v-list-item>
										<v-checkbox
											v-model="filters.unpatrolled"
											:label="$t( 'recentchanges-action-unpatrolled' )"
										/>
									</v-list-item>
									<v-list-item>
										<v-checkbox
											v-model="filters.suppressed"
											:label="$t( 'recentchanges-action-suppressed' )"
										/>
									</v-list-item>
								</v-list>
							</v-menu>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
						>
							<DatePicker
								v-model="filters.date_created_after"
								:label="$t( 'datepicker-startdate' )"
								suffix="T00:00Z"
							/>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
						>
							<DatePicker
								v-model="filters.date_created_before"
								:label="$t( 'datepicker-enddate' )"
								suffix="T23:59:59.999Z"
							/>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
							class="mt-2"
						>
							<v-btn
								color="primary base100--text"
								block
								:small="$vuetify.breakpoint.smAndDown"
								@click="filterChanges"
							>
								{{ $t( 'recentchanges-filter' ) }}
								<v-icon
									dark
									right
								>
									mdi-magnify
								</v-icon>
							</v-btn>
						</v-col>
						<v-col cols="6"
							lg="2"
							md="3"
							class="mt-2"
						>
							<v-btn
								block
								:small="$vuetify.breakpoint.smAndDown"
								@click="clearFilters"
							>
								{{ $t( 'clear' ) }}
								<v-icon
									dark
									right
								>
									mdi-close
								</v-icon>
							</v-btn>
						</v-col>
					</v-row>
				</v-form>
			</v-col>
		</v-row>

		<v-row v-if="!loading && numChanges === 0">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'recentchanges-nochangesfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<Revisions
					:revisions="recentChanges"
					aggregate
					@update-revisions="fetchRecentChanges"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-pagination
					v-if="numChanges > 0"
					v-model="filters.page"
					:length="Math.ceil( numChanges / itemsPerPage )"
					class="ma-4"
					total-visible="5"
					@input="goToPage"
				/>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import { fetchMetaInfo } from '@/helpers/metadata';
import { filterEmpty } from '@/helpers/object';
import DatePicker from '@/components/common/DatePicker';
import Revisions from '@/components/common/Revisions';

export default {
	name: 'RecentChanges',
	components: {
		DatePicker,
		Revisions
	},
	data() {
		return {
			itemsPerPage: 10,
			loading: true,
			filters: {
				user: null,
				target_type: null,
				suppressed: null,
				unpatrolled: null,
				date_created_after: null,
				date_created_before: null,
				page: 1
			}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'recentchanges' );
	},
	computed: {
		...mapState( 'recentchanges', [ 'recentChanges', 'numChanges' ] ),
		/**
		 * Format unpatrolled and suppressed>
		 *
		 * @return {string} - e.g. 'unpatrolled, suppressed'
		 */
		formattedActions() {
			let values = {
				unpatrolled: this.filters.unpatrolled,
				suppressed: this.filters.suppressed
			};
			values = Object.keys( values ).map( ( key ) => {
				if ( values[ key ] === true ) {
					// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
					return this.$t( `recentchanges-action-${key}` );
				} else {
					return '';
				}
			} );
			values = values.filter( ( each ) => each );
			return values.join( ' ' );
		},
		targetsComputed() {
			return [
				{
					type: 'tool',
					label: this.$t( 'recentchanges-targettype-tool' )
				},
				{
					type: 'toollist',
					label: this.$t( 'recentchanges-targettype-toollist' )
				}
			];
		}
	},
	methods: {
		fetchRecentChanges() {
			this.loading = true;
			this.$store.dispatch(
				'recentchanges/fetchRecentChanges', this.filters
			).then( () => {
				this.loading = false;
				this.$router.push( {
					name: 'recentchanges',
					query: filterEmpty( this.filters )
				} ).catch( () => {} );
			} );
		},
		goToPage( page ) {
			this.filters.page = page;
			this.fetchRecentChanges();
		},
		filterChanges() {
			this.filters.page = 1;
			this.fetchRecentChanges();
		},
		clearFilters() {
			this.filters = {
				user: null,
				target_type: null,
				suppressed: null,
				unpatrolled: null,
				date_created_after: null,
				date_created_before: null,
				page: 1
			};
			this.$refs.filtersform.reset();
			this.fetchRecentChanges();
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
					case 'user':
						this.filters.user = value;
						gotQueryData = true;
						break;
					case 'target_type':
						this.filters.target_type = value;
						gotQueryData = true;
						break;
					case 'suppressed':
						if ( value === 'true' ) {
							this.filters.suppressed = true;
							gotQueryData = true;
						} else if ( value === 'false' ) {
							this.filters.suppressed = false;
							gotQueryData = true;
						}
						break;
					case 'patrolled':
						if ( value === 'true' ) {
							this.filters.unpatrolled = false;
							gotQueryData = true;
						} else if ( value === 'false' ) {
							this.filters.unpatrolled = true;
							gotQueryData = true;
						}
						break;
					case 'date_created_after':
						this.filters.date_created_after = value;
						gotQueryData = true;
						break;
					case 'date_created_before':
						this.filters.date_created_before = value;
						gotQueryData = true;
						break;
					case 'page':
						this.filters.page = parseInt( value, 10 );
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
	mounted() {
		this.loadStateFromQueryString();
		this.fetchRecentChanges();
	}
};
</script>
