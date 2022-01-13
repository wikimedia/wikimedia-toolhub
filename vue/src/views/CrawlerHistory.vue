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
						<a :href="item.url.url" target="_blank">{{ item.url.url }}</a>
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
import customSort from '@/plugins/sort.js';
import fetchMetaInfo from '@/helpers/metadata';
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
			firstRowActive: true,
			rowSelected: false,
			expanded: []
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
		changeUrlsCrawled( item ) {
			this.crawlerRunEndDate = this.$moment.utc( item.end_date ).format( 'lll' );
			this.crawlerRunId = item.id;
			this.fetchCrawlerUrls();
		},
		crawlerRunRowClicked( item, row ) {
			row.select( true );
			this.rowSelected = true;
			this.firstRowActive = false;
			this.urlsPage = 1;
			this.changeUrlsCrawled( item );
			this.$vuetify.goTo( this.$refs.crawldetails );
		}
	},
	watch: {
		crawlerHistory( newVal, oldVal ) {
			if ( oldVal !== newVal ) {
				this.changeUrlsCrawled( this.crawlerHistory[ 0 ] );
			}
		}
	},
	mounted() {
		this.fetchCrawlerHistory();
	}
};
</script>
