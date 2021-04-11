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
		<v-row justify="space-around">
			<v-col v-for="tool in toolsList"
				:key="tool.name"
				sm="6"
				md="4"
				lg="3"
				cols="12"
			>
				<ToolCard :tool="tool" />
			</v-col>
		</v-row>

		<v-pagination
			v-if="numTools > 0"
			v-model="page"
			:length="Math.ceil( numTools / itemsPerPage )"
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
import ToolCard from '@/components/tools/ToolCard';

export default {
	components: {
		SearchBar,
		ToolCard
	},
	data: () => ( {
		page: 1,
		itemsPerPage: 12
	} ),
	computed: {
		...mapState( 'tools', [ 'toolsList', 'numTools' ] ),
		...mapState( 'crawler', [ 'crawlerHistory', 'lastCrawlerRun', 'numCrawlerRuns' ] )
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
		fetchCrawlerHistory() {
			this.$store.dispatch( 'crawler/fetchCrawlerHistory', 1 );
		},
		goToPage( num ) {
			const query = { page: parseInt( num ) || 1 };
			// Update query string and let our watch trigger a search
			this.$router.push( { query } ).catch( () => {} );
		},
		formatDate( date ) {
			return this.$moment( date ).format( 'lll' );
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
			this.listAllTools();
		}
	},
	mounted() {
		this.page = parseInt( this.$route.query.page ) || 1;
		this.listAllTools();
		this.fetchCrawlerHistory();
	}
};
</script>
