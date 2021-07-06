<template>
	<v-container>
		<v-row>
			<v-col cols="12" class="pa-0">
				<v-row no-gutters>
					<v-col sm="auto" cols="12">
						<v-avatar
							class="ma-3"
							size="150"
							tile
						>
							<v-img src="/static/img/logo-community.svg" />
						</v-avatar>
					</v-col>

					<v-col>
						<h1 class="text-h4 ma-1">
							{{ $t( 'welcomemessage' ) }}
						</h1>
						<div class="text-subtitle-1 mx-1">
							{{ $t( 'tagline-about' ) }}
						</div>

						<dl v-if="lastCrawlerRun" class="row ma-1">
							<dt class="me-1">
								<v-icon size="20">
									mdi-tools
								</v-icon>
								{{ $t( 'toolsfound', [ numTools ] ) }}
							</dt>
							<dd>
								<v-icon
									size="21"
								>
									mdi-update
								</v-icon>
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
							</dd>
						</dl>
					</v-col>
				</v-row>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<SearchBar
					@search="onSearchBarSearch"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in featuredLists.results"
				:key="list.title"
				class="lists"
				cols="12"
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
import ListView from '@/components/lists/ListView';

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
