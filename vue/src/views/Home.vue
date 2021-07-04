<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<SearchBar
					@search="onSearchBarSearch"
				/>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<v-card
					class="mx-auto"
					outlined
					elevation="1"
				>
					<v-row no-gutters>
						<v-col>
							<h2 class="text-h4 ma-4">
								{{ $t( 'welcomemessage' ) }}
							</h2>
							<div class="me-4 ms-4">
								{{ $t( 'tagline-about' ) }}
							</div>
							<div class="me-4 ms-4">
								<a href="https://meta.wikimedia.org/wiki/Toolhub"
									target="_blank"
								>
									{{ $t( 'tagline-learnmore' ) }}
								</a>
							</div>

							<v-row
								v-if="lastCrawlerRun"
								class="mx-1 my-3 text--secondary text-subtitle-2"
							>
								<v-col
									lg="6"
									cols="12"
									class="py-0"
								>
									<v-icon size="15">
										mdi-tools
									</v-icon>
									{{ $t( 'toolsfound', [ numTools ] ) }}
								</v-col>
								<v-col
									lg="6"
									cols="12"
									class="py-0"
								>
									<v-icon
										size="16"
										class="me-1"
									>
										mdi-update
									</v-icon>

									<a href="/crawler-history">
										{{ $t(
											'newtoolsfound',
											[
												lastCrawlerRun.new_tools +
													lastCrawlerRun.updated_tools
											]
										) }}
										{{ $t(
											'tools-lastupdated',
											[
												formatDate(
													lastCrawlerRun.end_date
												)
											]
										) }}
									</a>
								</v-col>
							</v-row>
						</v-col>
						<v-col cols="auto">
							<v-avatar
								class="ma-3"
								size="125"
								tile
							>
								<v-img src="/static/img/logo-community.svg" />
							</v-avatar>
						</v-col>
					</v-row>
				</v-card>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in featuredLists.results"
				:key="list.title"
				class="featured-lists"
			>
				<ListView :list="list" />
			</v-col>
		</v-row>

		<v-pagination
			v-if="featuredLists.count > 0"
			v-model="page"
			:length="Math.ceil( featuredLists.count / itemsPerPage )"
			class="ma-4"
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import '@/assets/styles/index.css';
import SearchBar from '@/components/search/SearchBar';
import fetchMetaInfo from '@/helpers/metadata';
import ListView from '@/components/tools/ListView';

export default {
	components: {
		SearchBar,
		ListView
	},
	data: () => ( {
		page: 1,
		itemsPerPage: 10
	} ),
	metaInfo() {
		return fetchMetaInfo( 'home' );
	},
	computed: {
		...mapState( 'tools', [ 'numTools' ] ),
		...mapState( 'crawler', [ 'crawlerHistory', 'lastCrawlerRun', 'numCrawlerRuns' ] ),
		...mapState( 'lists', [ 'featuredLists' ] )
	},
	methods: {
		onSearchBarSearch( query ) {
			this.$router.push( {
				name: 'search',
				query: { q: query }
			} );
		},
		listAllTools() {
			this.$store.dispatch( 'tools/listAllTools', this.page );
		},
		getFeaturedLists() {
			this.$store.dispatch( 'lists/getFeaturedLists', this.page );
		},
		fetchCrawlerHistory() {
			this.$store.dispatch( 'crawler/fetchCrawlerHistory', 1 );
		},
		goToPage( num ) {
			const query = { page: parseInt( num ) || 1 };
			// Update query string and let our watch trigger a search
			this.$router.push( { query } ).catch( () => {} );
		},
		formatDate( date ) {
			return this.$moment.utc( date ).format( 'lll' );
		}
	},
	watch: {
		/**
		 * Watch ?page=... and update displayed tools.
		 *
		 * @param {string} newValue
		 */
		'$route.query.page'( newValue ) {
			this.page = parseInt( newValue ) || 1;
			this.getFeaturedLists();
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;
		// Obtain the total number of tools currently available
		this.listAllTools();
		// Obtain the number of crawler runs and last update
		this.fetchCrawlerHistory();
		this.getFeaturedLists();
	}
};
</script>
