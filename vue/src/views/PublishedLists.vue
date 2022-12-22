<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<h2 class="text-h4">
					{{ $t( 'publishedlists' ) }}
				</h2>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12" class="py-0">
				<p>{{ $t( 'publishedlists-pagetitle' ) }}</p>
			</v-col>
		</v-row>

		<v-row>
			<v-col cols="12">
				<SearchBar
					ref="searchbar"
					:loading="searching"
					:target="searchTarget"
					@search="onSearchBarSearch"
				/>
			</v-col>
		</v-row>
		<v-row>
			<v-col cols="6">
				<p v-if="!searching && response.count">
					{{ $t( 'search-result-summary', [
						1 + pageOffset,
						pageOffset + response.results.length,
						response.count
					] ) }}
				</p>
				<p v-if="!searching && response.count === 0">
					{{ $t( 'search-no-results-message' ) }}
				</p>
			</v-col>
			<v-col cols="6">
				<Sort
					:order="queryParams.ordering"
					@change="onSortChange"
				/>
			</v-col>
		</v-row>

		<Lists
			:lists="response"
			list-footer
		/>
		<v-pagination
			v-if="response.count > 0"
			v-model="queryParams.page"
			:length="Math.ceil( response.count / queryParams.pageSize )"
			class="ma-4"
			total-visible="10"
			@input="goToPage"
		/>
	</v-container>
</template>

<script>
import fetchMetaInfo from '@/helpers/metadata';
import { mapState } from 'vuex';
import Lists from '@/components/lists/Lists';
import SearchBar from '@/components/search/SearchBar';
import Sort from '@/components/search/Sort';

export default {
	name: 'PublishedLists',
	components: {
		Lists,
		SearchBar,
		Sort
	},
	data() {
		return {
			searchTarget: 'list',
			searching: false,
			queryParams: {
				query: '',
				page: 1,
				pageSize: 10,
				ordering: '-modified_date'
			}
		};
	},
	metaInfo() {
		return fetchMetaInfo( 'publishedlists' );
	},
	computed: {
		...mapState( 'search', {
			response: 'listsResponse'
		} ),
		...mapState( 'lists', [ 'myLists' ] ),
		pageOffset() {
			return this.queryParams.pageSize * ( this.queryParams.page - 1 );
		}
	},
	methods: {
		pushQueryParamsToRouter() {
			const query = {
				q: this.queryParams.query,
				page: this.queryParams.page,
				page_size: this.queryParams.pageSize,
				ordering: this.queryParams.ordering
			};
			this.$router.push( { query } ).catch( () => {} );
		},
		onSearchBarSearch( query ) {
			this.queryParams.query = query;
			this.queryParams.page = 1;
			this.pushQueryParamsToRouter();
		},
		onSortChange( obj ) {
			this.queryParams.ordering = obj.value;
			this.queryParams.page = 1;
			this.pushQueryParamsToRouter();
		},
		findLists() {
			this.searching = true;
			this.$store.dispatch( 'search/findLists', this.queryParams )
				.finally( () => {
					this.searching = false;
				} );
		},
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
					case 'q':
						this.queryParams.query = value;
						this.$refs.searchbar.query = value;
						gotQueryData = true;
						break;
					case 'page':
						this.queryParams.page = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'page_size':
						this.queryParams.pageSize = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'ordering':
						this.queryParams.ordering = value;
						gotQueryData = true;
						break;
					default:
						// ignore this param
						break;
				}
			}
			return gotQueryData;
		},
		goToPage( num ) {
			const query = {};

			const params = new URLSearchParams(
				document.location.search.substring( 1 )
			);

			for ( const [ key, value ] of params ) {
				if ( value === undefined ) {
					continue;
				}
				query[ key ] = value;
			}

			query.page = parseInt( num, 10 ) || 1;

			this.$router.push( { query } ).catch( () => {} );
		}
	},
	watch: {
		/**
		 * Watch url query params,
		 * load query params into local state,
		 * then call findLists with the params.
		 *
		 * @param {string} newParams
		 */
		'$route.query': {
			handler( newParams ) {
				if ( newParams === undefined ) {
					return;
				}
				this.loadStateFromQueryString();
				this.findLists();
			},
			deep: true
		},
		myLists() {
			this.findLists();
		}
	},
	mounted() {
		if ( this.loadStateFromQueryString() ) {
			// Deep link, trigger a search now.
			this.findLists();
		} else {
			// Set query string based on internal state.
			// Our watch on $route.query will fire the search next.
			this.pushQueryParamsToRouter();
		}
	}
};
</script>
