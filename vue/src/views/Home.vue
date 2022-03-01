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
						<h1 class="text-h4 mx-1 my-3">
							{{ $t( 'welcomemessage' ) }}
						</h1>

						<div class="text-subtitle-1 ma-1">
							{{ $t( 'tagline-about' ) }}
						</div>

						<div v-if="totalTools" class="text-subtitle-1 ma-1">
							<v-icon
								size="20"
								color="base20"
							>
								mdi-update
							</v-icon>
							{{ $t( 'newtoolsfound', [ lastCrawlChanged ] ) }}
							{{ $t(
								'tools-lastupdated',
								[ formatDate( lastCrawlTime ) ]
							) }}
						</div>

						<div v-if="totalTools" class="text-subtitle-1 ma-1">
							<v-icon
								size="20"
								color="base20"
							>
								mdi-tools
							</v-icon>
							{{ $t( 'toolsfound', [ totalTools ] ) }}
						</div>
					</v-col>
				</v-row>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="12">
				<SearchBar
					:target="searchTarget"
					@search="onSearchBarSearch"
				/>
			</v-col>
		</v-row>

		<v-row>
			<v-col v-for="list in featuredLists.results"
				:key="list.title"
				cols="12"
				class="featured-lists"
			>
				<ListCard :list="list" />
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
import { mapActions, mapState } from 'vuex';
import '@/assets/styles/index.css';
import SearchBar from '@/components/search/SearchBar';
import fetchMetaInfo from '@/helpers/metadata';
import ListCard from '@/components/lists/ListCard';

export default {
	components: {
		ListCard,
		SearchBar
	},
	data: () => ( {
		searchTarget: 'tool',
		page: 1,
		itemsPerPage: 10
	} ),
	metaInfo() {
		return fetchMetaInfo( 'home' );
	},
	computed: {
		...mapState( 'ui', [
			'totalTools', 'lastCrawlTime', 'lastCrawlChanged'
		] ),
		...mapState( 'lists', [ 'featuredLists' ] )
	},
	methods: {
		...mapActions( 'ui', [ 'getHomeData' ] ),
		onSearchBarSearch( query ) {
			this.$router.push( {
				name: 'search',
				query: { q: query }
			} );
		},
		getFeaturedLists() {
			this.$store.dispatch( 'lists/getFeaturedLists', this.page );
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
		this.getHomeData();
		this.getFeaturedLists();
	}
};
</script>
