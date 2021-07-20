<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'auditlogs' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'auditlogs-pagetitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-form ref="filtersform">
				<v-row>
					<v-col cols="6"
						sm="3"
						md="2"
					>
						<v-text-field
							v-model="filters.user"
							:label="$t( 'auditlogs-username' )"
							prepend-icon="mdi-account-outline"
						/>
					</v-col>
					<v-col cols="6"
						sm="3"
						md="2"
					>
						<v-select
							v-model="filters.target_type"
							:label="$t( 'auditlogs-type' )"
							:items="targets"
							item-value="type"
							item-text="label"
							prepend-icon="mdi-filter-variant"
						/>
					</v-col>
					<v-col cols="6"
						sm="3"
						md="2"
					>
						<DatePicker
							ref="after"
							v-model="filters.after"
							:label="$t( 'datepicker-startdate' )"
							suffix="T00:00Z"
						/>
					</v-col>
					<v-col cols="6"
						sm="3"
						md="2"
					>
						<DatePicker
							ref="before"
							v-model="filters.before"
							:label="$t( 'datepicker-enddate' )"
							suffix="T23:59:59.999Z"
						/>
					</v-col>
					<v-col cols="6"
						sm="3"
						md="2"
						class="mt-2"
					>
						<v-btn
							color="primary base100--text"
							block
							@click="filterLogs"
						>
							{{ $t( 'auditlogs-filter' ) }}
							<v-icon
								dark
								right
							>
								mdi-magnify
							</v-icon>
						</v-btn>
					</v-col>
					<v-col cols="6"
						sm="3"
						md="2"
						class="mt-2"
					>
						<v-btn
							block
							@click="clearFilters"
						>
							{{ $t( 'auditlogs-clear' ) }}
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
		</v-row>

		<v-row v-if="!loading && numLogs === 0">
			<v-col cols="12">
				<p class="text-h6 text--secondary">
					{{ $t( 'auditlogs-nologsfoundtext' ) }}
				</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<LogEvent
					v-for="log in auditLogs"
					:key="log.id"
					:log="log"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<v-pagination
					v-if="numLogs > 0"
					v-model="page"
					:length="Math.ceil( numLogs / itemsPerPage )"
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
import LogEvent from '@/components/auditlog/LogEvent';

export default {
	components: {
		DatePicker,
		LogEvent
	},
	data() {
		return {
			page: 1,
			itemsPerPage: 10,
			loading: true,
			filters: {
				user: null,
				target_type: null,
				after: null,
				before: null
			},
			targets: [
				{
					type: 'tool',
					label: this.$t( 'auditlogs-targettype-tool' )
				},
				{
					type: 'url',
					label: this.$t( 'auditlogs-targettype-url' )
				},
				{
					type: 'user',
					label: this.$t( 'auditlogs-targettype-user' )
				},
				{
					type: 'group',
					label: this.$t( 'auditlogs-targettype-group' )
				},
				{
					type: 'version',
					label: this.$t( 'auditlogs-targettype-version' )
				},
				{
					type: 'toollist',
					label: this.$t( 'auditlogs-targettype-toollist' )
				}
			]
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'auditlogs' );
	},
	computed: {
		...mapState( 'auditlogs', [ 'auditLogs', 'numLogs' ] )
	},
	methods: {
		fetchAuditLogs() {
			this.loading = true;
			this.$store.dispatch( 'auditlogs/fetchAuditLogs', {
				page: this.page,
				filters: this.filters
			} ).then( () => {
				this.loading = false;
				this.$router.push( {
					path: '/audit-logs',
					query: filterEmpty( this.filters )
				} ).catch( () => {} );
			} );
		},
		goToPage( page ) {
			this.page = page;
			this.fetchAuditLogs();
		},
		filterLogs() {
			this.page = 1;
			this.fetchAuditLogs();
		},
		clearFilters() {
			this.filters = {
				user: null,
				target_type: null,
				after: null,
				before: null
			};
			this.$refs.filtersform.reset();
			this.fetchAuditLogs();
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
					case 'after':
						this.filters.after = value;
						gotQueryData = true;
						break;
					case 'before':
						this.filters.before = value;
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
	mounted() {
		this.loadStateFromQueryString();
		this.fetchAuditLogs();
	}
};
</script>
