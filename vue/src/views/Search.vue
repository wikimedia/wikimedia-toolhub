<template>
	<v-container>
		<v-row>
			<v-col cols="12">
				<SearchBar
					ref="searchbar"
					:loading="searching"
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
					{{ $t( 'search-no-results-message') }}
				</p>
			</v-col>
			<v-col cols="6">
				<Sort
					ref="sort"
					@change="onSortChange"
				/>
			</v-col>
		</v-row>
		<v-row>
			<v-col
				md="3"
				cols="12"
			>
				<Filters
					:facets="response.facets"
					@change="onFilterChange"
				/>
			</v-col>
			<v-col
				md="9"
				cols="12"
			>
				<v-row justify="space-around">
					<v-col v-for="tool in response.results"
						:key="tool.name"
						sm="12"
						md="6"
						lg="4"
						cols="12"
					>
						<ToolCard :tool="tool" />
					</v-col>
				</v-row>
				<v-row>
					<v-col cols="12">
						<v-pagination
							v-if="!searching && response.count > 0"
							v-model="page"
							:length="Math.ceil( response.count / pageSize )"
							class="ma-4"
							total-visible="5"
							@input="onPageChange"
						/>
					</v-col>
				</v-row>
			</v-col>
		</v-row>
	</v-container>
</template>

<script>
import { mapState } from 'vuex';
import { ensureArray } from '@/utils';
import Filters from '@/components/search/Filters';
import SearchBar from '@/components/search/SearchBar';
import Sort from '@/components/search/Sort';
import ToolCard from '@/components/tools/ToolCard';

export default {
	name: 'Search',
	components: {
		Filters,
		SearchBar,
		Sort,
		ToolCard
	},
	data: () => ( {
		query: '',
		page: 1,
		pageSize: 12,
		facets: [],
		searching: false,
		ordering: '-score'
	} ),
	computed: {
		...mapState( 'search', {
			response: 'toolsResponse',
			queryParams: 'toolsQueryParams'
		} ),
		pageOffset() {
			return this.pageSize * ( this.page - 1 );
		}
	},
	methods: {
		onSearchBarSearch( query ) {
			this.query = query;
			this.page = 1;
			this.doSearch();
		},
		onSortChange( obj ) {
			this.ordering = obj.value;
			this.page = 1;
			this.doSearch();
		},
		onPageChange( page ) {
			this.page = page;
			this.doSearch();
		},
		onFilterChange( payload ) {
			this.facets = payload;
			this.page = 1;
			this.doSearch();
		},
		doSearch() {
			const payload = {
				query: this.query,
				page: this.page,
				pageSize: this.pageSize,
				ordering: this.ordering,
				filters: this.facets
			};
			this.searching = true;
			this.$store.dispatch( 'search/findTools', payload );
		},
		/**
		 * Allow deep linking to search results by reconstructing internal
		 * state based on data provided in the current query string.
		 *
		 * @return {boolean} True if state was updated. False otherwise.
		 */
		loadStateFromQueryString() {
			const params = new URLSearchParams(
				document.location.search.substring( 1 )
			);
			let gotQueryData = false;
			const qsFilters = [];
			for ( const [ key, value ] of params ) {
				if ( value === undefined ) {
					continue;
				}
				switch ( key ) {
					case 'q':
						this.query = value;
						this.$refs.searchbar.setQuery( value );
						gotQueryData = true;
						break;
					case 'page':
						this.page = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'page_size':
						this.pageSize = parseInt( value, 10 );
						gotQueryData = true;
						break;
					case 'ordering':
						this.ordering = value;
						this.$refs.sort.setOrder( value );
						gotQueryData = true;
						break;
					case 'uselang':
						// ignore global state params
						break;
					default:
						// Treat any unknown param as a search filter coming
						// from our facet navigation. This could be made
						// 'smarter' if we loaded the OpenAPI schema for the
						// search endpoint and used it to validate param
						// names.
						ensureArray( value ).forEach( ( val ) => {
							qsFilters.push( [ key, val ] );
						} );
						break;
				}
			}
			if ( qsFilters.length > 0 ) {
				this.facets = qsFilters;
				gotQueryData = true;
			}
			return gotQueryData;
		}
	},
	watch: {
		/**
		 * React to changes in stored query parameters.
		 *
		 * @param {URLSearchParams} newParams
		 * @param {URLSearchParams|null} oldParams
		 */
		queryParams( newParams, oldParams ) { // eslint-disable-line no-unused-vars
			if ( newParams === undefined ) {
				return;
			}
			const query = {};
			for ( const key of newParams.keys() ) {
				query[ key ] = newParams.getAll( key );
			}
			this.searching = false;
			this.$router.push( { query } ).catch( () => {} );
		}
	},
	/**
	 * Watch for the 'mounted' lifecycle event.
	 */
	mounted() {
		if ( !this.searching ) {
			if ( this.loadStateFromQueryString() ) {
				this.doSearch();
			}
		}
	}
};
</script>
