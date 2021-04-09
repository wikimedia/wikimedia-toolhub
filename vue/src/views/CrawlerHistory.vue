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
				:class="{ active: firstRowActive, selected: rowSelected }"
			>
				<v-data-table
					:headers="crawlerRunsHeaders"
					:page="runsPage"
					:items-per-page="itemsPerPage"
					:items="crawlerHistory"
					class="elevation-0 mt-2 table-striped"
					hide-default-footer
					mobile-breakpoint="0"
					:custom-sort="customSortHistory"
					single-select
					:loading="numCrawlerRuns === 0"
					@click:row="crawlerRunRowClicked"
				>
					<template #[`item.end_date`]="{ item }">
						{{ item.end_date | moment( "lll" ) }}
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
						<chart :height="250" :chart-data="crawledUrlsChartData" />
					</v-col>
					<v-col cols="12"
						md="6"
						lg="12"
					>
						<chart :height="250" :chart-data="totalToolsChartData" />
					</v-col>
				</v-row>
			</v-col>
		</v-row>

		<v-row
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
					:page="urlsPage"
					:items-per-page="itemsPerPage"
					:items="crawlerUrls"
					:expanded.sync="expanded"
					item-key="url.url"
					show-expand
					single-expand
					class="elevation-0 mt-2 table-striped"
					hide-default-footer
					mobile-breakpoint="0"
					:custom-sort="customSortHistory"
					:loading="numCrawlerUrls === 0"
				>
					<template #[`item.url.url`]="{ item }">
						<a :href="`${item.url.url}`" target="_blank">{{ item.url.url }}</a>
					</template>

					<template #[`item.url.created_by.username`]="{ item }">
						<a :href="`http://meta.wikimedia.org/wiki/User:${item.url.created_by.username}`"
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
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import Chart from '@/components/chart/LineChart.js';
import customSort from '@/plugins/sort.js';

export default {
	components: { Chart },
	data() {
		return {
			runsPage: 1,
			urlsPage: 1,
			itemsPerPage: 10,
			totalToolsChartData: null,
			crawledUrlsChartData: null,
			crawlerRunEndDate: null,
			crawlerRunId: 0,
			firstRowActive: true,
			rowSelected: false,
			expanded: []
		};
	},
	computed: {
		...mapState( 'crawler', [
			'crawlerHistory',
			'numCrawlerRuns',
			'crawlerUrls',
			'numCrawlerUrls'
		] ),

		clonedHistory() {
			return this.crawlerHistory;
		},

		crawlerRunsHeaders() {
			return [
				{
					text: this.$t( 'crawlerrundate' ),
					value: 'end_date',
					sortable: true
				},
				{
					text: this.$t( 'urlscrawled' ),
					value: 'urls.count',
					sortable: true
				},
				{
					text: this.$t( 'totaltools' ),
					value: 'total_tools',
					sortable: true
				}
			];
		},

		urlsCrawledHeaders() {
			return [
				{
					text: this.$t( 'url' ),
					value: 'url.url',
					sortable: true
				},
				{
					text: 'Created By',
					value: 'url.created_by.username',
					sortable: true
				},
				{
					text: 'Status',
					value: 'valid',
					sortable: true
				},
				{
					text: '',
					value: 'data-table-expand'
				}
			];
		}
	},
	methods: {
		fetchCrawlerHistory() {
			this.$store.dispatch( 'crawler/fetchCrawlerHistory', this.runsPage );
		},
		fetchCrawlerUrls() {
			this.$store.dispatch( 'crawler/fetchCrawlerUrls', { page: this.urlsPage, runId: this.crawlerRunId } );
		},
		goToRunsPage( page ) {
			this.runsPage = page;
			this.fetchCrawlerHistory();
			this.firstRowActive = true;
			this.rowSelected = false;
		},
		goToUrlsPage( page ) {
			this.urlsPage = page;
			this.fetchCrawlerUrls();
		},
		customSortHistory( items, index, isDesc ) {
			const sortedItems = customSort( items, index, isDesc );
			return sortedItems;
		},
		fillChartsData() {
			this.crawledUrlsChartData = {
				labels: this.getEndDates(),
				datasets: [
					{
						label: this.$t( 'urlscrawled' ),
						backgroundColor: this.$vuetify.theme.themes.light.accent,
						data: this.getUrlsCrawled()
					}
				]
			};

			this.totalToolsChartData = {
				labels: this.getEndDates(),
				datasets: [
					{
						label: this.$t( 'totaltools' ),
						backgroundColor: this.$vuetify.theme.themes.light.primary,
						data: this.getTotalTools()
					}
				]
			};
		},
		getEndDates() {
			const endDates = [];

			this.crawlerHistory.forEach( ( history ) => {
				endDates.push( this.$moment( history.end_date ).format( 'lll' ) );
			} );

			return endDates.reverse();
		},
		getTotalTools() {
			const totalTools = [];

			this.crawlerHistory.forEach( ( history ) => {
				totalTools.push( history.total_tools );
			} );

			return totalTools.reverse();
		},
		getUrlsCrawled() {
			const crawledUrls = [];

			this.crawlerHistory.forEach( ( history ) => {
				crawledUrls.push( history.urls.count );
			} );

			return crawledUrls.reverse();
		},
		changeUrlsCrawled( item ) {
			this.crawlerRunEndDate = this.$moment( item.end_date ).format( 'lll' );
			this.crawlerRunId = item.id;
			this.fetchCrawlerUrls();
		},
		crawlerRunRowClicked( item, row ) {
			row.select( true );
			this.rowSelected = true;
			this.firstRowActive = false;
			this.urlsPage = 1;
			this.changeUrlsCrawled( item );
		}
	},
	watch: {
		clonedHistory( newVal, oldVal ) {
			if ( oldVal !== newVal ) {
				this.fillChartsData();
				this.changeUrlsCrawled( this.crawlerHistory[ 0 ] );
			}
		}
	},
	mounted() {
		this.fetchCrawlerHistory();
	}
};
</script>
