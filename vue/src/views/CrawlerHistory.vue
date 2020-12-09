<template>
	<v-container>
		<v-row>
			<v-col cols="12"
				class="pa-0 mt-2"
			>
				<h2 class="display-1">
					{{ $t( 'crawlerhistory' ) }}
				</h2>
			</v-col>

			<v-col cols="12"
				class="pa-0 mt-2"
			>
				<p>{{ $t( 'crawlerhistory-pagesubtitle' ) }}</p>
			</v-col>

			<v-row
				class="elevation-2 mt-2 ma-1 pa-2 table-crawler-history"
			>
				<v-col cols="12">
					<h3 class="headline">
						{{ $t( 'crawlerruns' ) }}
					</h3>
				</v-col>
				<v-col
					lg="6"
					cols="12"
					:class="{ active: firstRowActive }"
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
						:loading="numCrawlerRuns > 0 || apiErrorMsg ? false : true"
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
							sm="6"
							md="6"
							lg="12"
						>
							<chart :height="250" :chart-data="crawledUrlsChartData" />
						</v-col>
						<v-col cols="12"
							sm="6"
							md="6"
							lg="12"
						>
							<chart :height="250" :chart-data="newToolsChartData" />
						</v-col>
					</v-row>
				</v-col>
			</v-row>

			<v-row
				class="elevation-2 mt-6 ma-1 pa-2"
			>
				<v-col cols="12">
					<h3 class="headline">
						{{ $t( 'urlscrawledon', { date: crawlerRunEndDate } ) }}
					</h3>
				</v-col>
				<v-col
					cols="12"
				>
					<v-data-table
						:headers="urlsCrawledHeaders"
						:page="urlsPage"
						:items-per-page="itemsPerPage"
						:items="crawlerUrls"
						class="elevation-0 mt-2 table-striped"
						hide-default-footer
						mobile-breakpoint="0"
						:custom-sort="customSortHistory"
						:loading="numCrawlerUrls > 0 || apiErrorMsg ? false : true"
					>
						<template #[`item.valid`]="{ item }">
							<p v-if="item.valid" class="success--text pa-0 ma-0">
								{{ $t( 'valid' ) }}
							</p>

							<p v-if="!item.valid" class="error--text pa-0 ma-0">
								{{ $t( 'invalid' ) }}
							</p>
						</template>

						<template #[`item.url.created_date`]="{ item }">
							{{ item.url.created_date | moment( "lll" ) }}
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
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import Chart from '@/components/chart/LineChart.js';
import customSort from '@/plugins/sort.js';
import moment from 'moment';

export default {
	components: { Chart },
	data() {
		return {
			runsPage: 1,
			urlsPage: 1,
			itemsPerPage: 10,
			newToolsChartData: null,
			crawledUrlsChartData: null,
			crawlerRunEndDate: null,
			crawlerRunId: 0,
			firstRowActive: true
		};
	},
	computed: {
		...mapState( 'crawler', [ 'crawlerHistory', 'apiErrorMsg', 'numCrawlerRuns',
			'crawlerUrls', 'numCrawlerUrls' ] ),

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
					text: this.$t( 'newtoolsadded' ),
					value: 'new_tools',
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
					text: this.$t( 'datecreated' ),
					value: 'url.created_date',
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
			this.firstRowActive = true;
			this.fetchCrawlerHistory();
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
			this.newToolsChartData = {
				labels: this.getEndDates(),
				datasets: [
					{
						label: this.$t( 'newtoolsadded' ),
						backgroundColor: this.$vuetify.theme.themes.light.accent,
						data: this.getNewToolsAdded()
					}
				]
			};

			this.crawledUrlsChartData = {
				labels: this.getEndDates(),
				datasets: [
					{
						label: this.$t( 'urlscrawled' ),
						backgroundColor: this.$vuetify.theme.themes.light.primary,
						data: this.getUrlsCrawled()
					}
				]
			};
		},
		getEndDates() {
			const endDates = [];

			this.crawlerHistory.forEach( ( history ) => {
				endDates.push( moment( history.end_date ).format( 'lll' ) );
			} );

			return endDates.reverse();
		},
		getNewToolsAdded() {
			const newToolsAdded = [];

			this.crawlerHistory.forEach( ( history ) => {
				newToolsAdded.push( history.new_tools );
			} );

			return newToolsAdded.reverse();
		},
		getUrlsCrawled() {
			const crawledUrls = [];

			this.crawlerHistory.forEach( ( history ) => {
				crawledUrls.push( history.urls.count );
			} );

			return crawledUrls.reverse();
		},
		changeUrlsCrawled( item ) {
			this.crawlerRunEndDate = moment( item.end_date ).format( 'lll' );
			this.crawlerRunId = item.id;
			this.fetchCrawlerUrls();
		},
		crawlerRunRowClicked( item, row ) {
			row.select( true );
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
