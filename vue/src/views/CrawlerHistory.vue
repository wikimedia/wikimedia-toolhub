<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'crawlerhistory' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'crawlerhistory-pagesubtitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row
			class="elevation-2 pa-2 mx-1 my-4 table-crawler-history"
		>
			<v-col cols="12">
				<h3 class="text-h5">
					{{ $t( 'crawlerruns' ) }}
				</h3>
			</v-col>
			<v-col
				lg="6"
				cols="12"
			>
				<v-data-table
					v-model="crawlerRunSelected"
					:headers="crawlerRunsHeaders"
					:items="crawlerHistory"
					:options.sync="crawlerHistoryOptions"
					:server-items-length="numCrawlerRuns"
					class="elevation-0 mt-2 table-striped"
					hide-default-footer
					mobile-breakpoint="0"
					single-select
					:loading="crawlerHistoryLoading"
					@click:row="crawlerRunRowClicked"
				>
					<template #[`item.end_date`]="{ item }">
						{{ item.end_date | moment( "utc", "lll" ) }}
					</template>
				</v-data-table>

				<v-pagination
					v-if="numCrawlerRuns > 0"
					v-model="runsPage"
					:length="Math.ceil( numCrawlerRuns / itemsPerPage )"
					class="ma-4"
					@input="goToRunsPage"
				/>
			</v-col>

			<v-col
				lg="6"
				cols="12"
			>
				<v-row>
					<v-col cols="12"
						md="6"
						lg="12"
					>
						<LineChart :height="250" :chart-data="crawledUrlsChartData" />
					</v-col>
					<v-col cols="12"
						md="6"
						lg="12"
					>
						<LineChart :height="250" :chart-data="totalToolsChartData" />
					</v-col>
				</v-row>
			</v-col>
		</v-row>

		<v-row
			ref="crawldetails"
			class="elevation-2 mx-1 my-4 pa-2"
		>
			<v-col cols="12">
				<h3 class="text-h5">
					{{ $t( 'urlscrawledon', [ crawlerRunEndDate ] ) }}
				</h3>
			</v-col>
			<v-col cols="12">
				<v-data-table
					:headers="urlsCrawledHeaders"
					:items="crawlerUrls"
					:options.sync="crawlerUrlsOptions"
					:server-items-length="numCrawlerUrls"
					:expanded.sync="expanded"
					item-key="url.url"
					show-expand
					single-expand
					class="elevation-0 mt-2 table-striped"
					hide-default-footer
					mobile-breakpoint="0"
					:loading="crawlerUrlsLoading"
				>
					<template #[`item.url.url`]="{ item }">
						<a :href="item.url.url" target="_blank">{{ item.url.url }}</a>
					</template>

					<template #[`item.url.created_by.username`]="{ item }">
						<a :href="`https://meta.wikimedia.org/wiki/User:${item.url.created_by.username}`"
							target="_blank"
						>{{ item.url.created_by.username }}</a>
					</template>

					<template #[`item.valid`]="{ item }">
						<span v-if="item.valid" class="success--text pa-0 ma-0">
							{{ $t( 'valid' ) }}
						</span>
						<span v-else class="error--text pa-0 ma-0">
							{{ $t( 'invalid' ) }}
						</span>
					</template>
					<template #expanded-item="{ headers, item }">
						<td
							class="pa-2"
							:colspan="headers.length"
						>
							<pre class="pre-logs">{{ item.logs }}</pre>
						</td>
					</template>
				</v-data-table>

				<v-pagination
					v-if="numCrawlerUrls > 0"
					v-model="urlsPage"
					:length="Math.ceil( numCrawlerUrls / itemsPerPage )"
					class="ma-4"
					@input="goToUrlsPage"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<ScrollTop />
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import LineChart from '@/components/chart/LineChart.js';
import fetchMetaInfo from '@/helpers/metadata';
import { filterEmpty } from '@/helpers/object';
import ScrollTop from '@/components/common/ScrollTop';

export default {
	components: {
		LineChart,
		ScrollTop
	},
	data() {
		return {
			runsPage: 1,
			urlsPage: 1,
			itemsPerPage: 10,
			crawlerRunEndDate: null,
			crawlerRunId: 0,
			crawlerRunSelected: [],
			expanded: [],
			crawlerUrlsLoading: null,
			crawlerHistoryLoading: null,
			crawlerUrlsFilters: {
				urls_ordering: null
			},
			crawlerHistoryFilters: {
				runs_ordering: null
			},
			crawlerUrlsOptions: {},
			crawlerHistoryOptions: {}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'crawlerhistory' );
	},
	computed: {
		crawledUrlsChartData() {
			return {
				labels: this.crawlEndDates,
				datasets: [
					{
						label: this.$t( 'urlscrawled' ),
						backgroundColor: this.$vuetify.theme.themes.light.accent,
						data: this.crawlUrlsCrawled
					}
				]
			};
		},
		totalToolsChartData() {
			return {
				labels: this.crawlEndDates,
				datasets: [
					{
						label: this.$t( 'totaltools' ),
						backgroundColor: this.$vuetify.theme.themes.light.primary,
						data: this.crawlTotalTools
					}
				]
			};
		},
		...mapState( 'crawler', [
			'crawlerHistory',
			'numCrawlerRuns',
			'crawlerUrls',
			'numCrawlerUrls'
		] ),
		crawlerRunsHeaders() {
			return [
				{
					text: this.$t( 'crawlerrundate' ),
					value: 'end_date'
				},
				{
					text: this.$t( 'urlscrawled' ),
					value: 'crawled_urls'
				},
				{
					text: this.$t( 'totaltools' ),
					value: 'total_tools'
				}
			];
		},
		urlsCrawledHeaders() {
			return [
				{
					text: this.$t( 'url' ),
					value: 'url.url'
				},
				{
					text: this.$t( 'createdby' ),
					value: 'url.created_by.username'
				},
				{
					text: this.$t( 'status' ),
					value: 'valid'
				},
				{
					text: '',
					value: 'data-table-expand'
				}
			];
		},
		crawlEndDates() {
			return this.crawlerHistory.map( ( crawl ) =>
				this.$moment.utc( crawl.end_date ).format( 'lll' )
			).reverse();
		},
		crawlTotalTools() {
			return this.crawlerHistory.map( ( crawl ) =>
				crawl.total_tools
			).reverse();
		},
		crawlUrlsCrawled() {
			return this.crawlerHistory.map( ( crawl ) =>
				crawl.crawled_urls
			).reverse();
		}
	},
	methods: {
		fetchCrawlerHistory() {
			this.crawlerHistoryLoading = true;
			this.$store.dispatch( 'crawler/fetchCrawlerHistory', {
				page: this.runsPage,
				filters: this.crawlerHistoryFilters
			} )
				.finally( () => { this.crawlerHistoryLoading = false; } );
		},
		fetchCrawlerUrls() {
			this.crawlerUrlsLoading = true;
			this.$store.dispatch( 'crawler/fetchCrawlerUrls',
				{ page: this.urlsPage,
					runId: this.crawlerRunId,
					filters: this.crawlerUrlsFilters
				} )
				.then( () => {
					this.$router.push( {
						path: document.location.pathname,
						query: filterEmpty( {
							runs_page: this.runsPage,
							urls_page: this.urlsPage,
							runs_id: this.crawlerRunId,
							...this.crawlerHistoryFilters,
							...this.crawlerUrlsFilters } )
					} ).catch( () => {} );
				} )
				.finally( () => { this.crawlerUrlsLoading = false; } );
		},
		goToRunsPage( page ) {
			this.runsPage = page;
			this.fetchCrawlerHistory();
		},
		goToUrlsPage( page ) {
			this.urlsPage = page;
			this.fetchCrawlerUrls();
		},
		changeUrlsCrawled() {
			let item = this.crawlerHistory.filter( ( run ) => run.id === this.crawlerRunId );
			if ( item.length === 0 ) {
				item = [ this.crawlerHistory[ 0 ] ];
				this.crawlerRunId = item[ 0 ].id;
			}
			this.crawlerRunEndDate = this.$moment.utc( item[ 0 ].end_date ).format( 'lll' );
			this.crawlerRunSelected = item;
			this.fetchCrawlerUrls();
		},
		crawlerRunRowClicked( item ) {
			this.crawlerRunId = item.id;
			this.urlsPage = 1;
			this.changeUrlsCrawled();
			this.$vuetify.goTo( this.$refs.crawldetails );
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
					case 'runs_page':
						this.runsPage = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'urls_page':
						this.urlsPage = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'runs_id':
						this.crawlerRunId = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'runs_ordering':
						this.crawlerHistoryFilters.runs_ordering = value;

						if ( value[ 0 ] === '-' ) {
							this.crawlerHistoryOptions.sortBy = [ value.replace( '-', '' ) ];
							this.crawlerHistoryOptions.sortDesc = [ true ];
						} else {
							this.crawlerHistoryOptions.sortBy = [ value ];
							this.crawlerHistoryOptions.sortDesc = [ false ];
						}

						gotQueryData = true;
						break;
					case 'urls_ordering':
						this.crawlerUrlsFilters.urls_ordering = value;

						if ( value[ 0 ] === '-' ) {
							this.crawlerUrlsOptions.sortBy = [
								value.replace( '-', '' ).split( '__' ).join( '.' ) ];
							this.crawlerUrlsOptions.sortDesc = [ true ];
						} else {
							this.crawlerUrlsOptions.sortBy = [ value.split( '__' ).join( '.' ) ];
							this.crawlerUrlsOptions.sortDesc = [ false ];
						}

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
		crawlerHistory( newVal, oldVal ) {
			if ( oldVal !== newVal ) {
				this.changeUrlsCrawled();
			}
		},
		crawlerHistoryOptions: {
			handler( _, oldVal ) {
				const {
					sortBy,
					sortDesc
				} = this.crawlerHistoryOptions;
				if ( sortBy.length === 1 && sortDesc.length === 1 ) {
					if ( sortDesc[ 0 ] === false ) {
						this.crawlerHistoryFilters.runs_ordering = sortBy[ 0 ];
					} else {
						this.crawlerHistoryFilters.runs_ordering = `-${sortBy[ 0 ]}`;
					}
					this.fetchCrawlerHistory();
				} else if ( oldVal.sortBy ) {
					this.crawlerHistoryFilters.runs_ordering = null;
					this.fetchCrawlerHistory();
				}
			},
			deep: true
		},
		crawlerUrlsOptions: {
			handler( _, oldVal ) {
				const {
					sortBy,
					sortDesc
				} = this.crawlerUrlsOptions;
				if ( oldVal.sortBy && sortBy.length === 1 && sortDesc.length === 1 ) {
					if ( sortDesc[ 0 ] === false ) {
						this.crawlerUrlsFilters
							.urls_ordering = sortBy[ 0 ].split( '.' ).join( '__' );
					} else {
						this.crawlerUrlsFilters
							.urls_ordering = `-${sortBy[ 0 ].split( '.' ).join( '__' )}`;
					}
					this.fetchCrawlerUrls();
				} else if ( oldVal.sortBy ) {
					this.crawlerUrlsFilters.urls_ordering = null;
					this.fetchCrawlerUrls();
				}
			},
			deep: true
		}
	},
	mounted() {
		this.loadStateFromQueryString();
		this.fetchCrawlerHistory();
	}
};
</script>
