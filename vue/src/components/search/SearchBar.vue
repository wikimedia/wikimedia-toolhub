<template>
	<v-combobox
		ref="combobox"
		v-model="query"
		class="searchbar"
		:label="getLabel()"
		:loading="loading || autoCompleteLoading"
		:search-input.sync="query"
		:menu-props="menuProps"
		:items="getAutoCompleteResultsArr()"
		solo
		no-filter
		clearable
		hide-details
		:hide-no-data="hideOnNoData"
		@keydown.enter="onEnterKey"
		@keyup.enter="onEnterKey"
		@click:clear="onClear"
		@change="routeToView"
	>
		<template #append>
			<v-btn
				icon
				@click="onSearch"
			>
				<v-icon
					aria-hidden="false"
					:aria-label="$t( 'search' )"
					role="img"
					color="base20"
					size="30"
				>
					mdi-magnify
				</v-icon>
			</v-btn>
		</template>
		<template #item="data">
			<v-list-item-content class="autocomplete">
				<v-list-item-title>
					<dl class="row ma-0">
						<dt class="me-4">{{ autoCompleteResults[data.item][0] }}</dt>
						<dd class="desc grey--text text--darken-1">
							{{ autoCompleteResults[data.item][1] }}
						</dd>
					</dl>
				</v-list-item-title>
			</v-list-item-content>
		</template>

		<template v-if="!autoCompleteLoading" #no-data>
			<v-list-item>
				<v-list-item-content>
					<v-list-item-title>
						{{ getNoDataString() }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
		</template>
	</v-combobox>
</template>

<script>
import { mapState } from 'vuex';

import { EventBus } from '@/helpers/event-bus';

const LIST = 'list';
const TOOL = 'tool';

function getLabel() {
	if ( this.target === TOOL ) {
		return this.$t( 'tools-search-label' );
	} else if ( this.target === LIST ) {
		return this.$t( 'lists-search-label' );
	}
}

function getNoDataString() {
	if ( this.target === TOOL ) {
		return this.$t( 'tool-not-found', [ this.query ] );
	} else if ( this.target === LIST ) {
		return this.$t( 'list-not-found', [ this.query ] );
	}
}

/**
 * Handle enter key keyup & keydown events.
 *
 * @param {Object} event - key event
 */
function onEnterKey( event ) {
	const path = this.$route.path;
	if ( event.type === 'keyup' && path === this.lastEnterPath ) {
		// Only trigger an actual search if other navigation has not fired
		// since the matching keydown event. This works around the keyup
		// event firing after we have already handled an autocomplete result
		// selection done via keyboard navigation.
		this.onSearch( event );
	} else if ( event.type === 'keydown' ) {
		// Track the page path for comparison when handling the keyup event.
		this.lastEnterPath = path;
	}
}

function onSearch() {
	this.$emit( 'search', this.query );
	this.hideOnNoData = true;
	if ( this.target === TOOL ) {
		this.$store.commit( 'search/onToolsAutoCompleteResults', {} );
	} else if ( this.target === LIST ) {
		this.$store.commit( 'search/onListsAutoCompleteResults', {} );
	}
}

function onClear( e ) {
	e.preventDefault();
	this.query = '';
	this.$emit( 'search', this.query );
}

function setQuery( query ) {
	this.query = query;
}

function performAutoComplete( query ) {
	if ( !query ) {
		return;
	}
	this.hideOnNoData = false;
	this.autoCompleteLoading = true;
	const vuexMethod = this.target === TOOL ?
		'search/autoCompleteTools' :
		'search/autoCompleteLists';
	this.$store.dispatch( vuexMethod, query ).finally(
		() => {
			this.autoCompleteLoading = false;
		}
	);
}

function routeToView( id ) {
	if ( id === null ) {
		return;
	}
	const params = {};
	let routeName;
	if ( this.target === TOOL ) {
		params.name = id;
		routeName = 'tools-view';
	} else if ( this.target === LIST ) {
		params.id = id;
		routeName = 'lists-view';
	}

	this.$refs.combobox.reset();
	this.$router.push( { name: routeName, params } );
}

function getAutoCompleteResultsArr() {
	return this.autoCompleteResults ?
		Object.keys( this.autoCompleteResults ) :
		[];
}

export default {
	name: 'SearchBar',
	props: {
		loading: {
			type: Boolean
		},
		target: {
			type: String,
			required: true,
			validator: function ( value ) {
				return [ LIST, TOOL ].indexOf( value ) !== -1;
			}
		}
	},
	data: () => ( {
		query: '',
		autoCompleteLoading: false,
		hideOnNoData: true,
		// TODO: find out why eslint is firing this false positive error
		// eslint-disable-next-line vue/no-unused-properties
		lastEnterPath: null
	} ),
	computed: {
		menuProps() {
			const contentClass = { contentClass: 'autocomplete-menu__content' };
			return !this.query ? { value: false, ...contentClass } : contentClass;
		},
		...mapState( 'search', {
			autoCompleteResults: function ( state ) {
				if ( this.target === TOOL ) {
					return state.toolAutoCompleteResults;
				} else if ( this.target === LIST ) {
					return state.listAutoCompleteResults;
				}
			}
		} )
	},
	methods: {
		getLabel,
		getNoDataString,
		onSearch,
		onClear,
		// eslint-disable-next-line vue/no-unused-properties
		setQuery,
		performAutoComplete,
		getAutoCompleteResultsArr,
		routeToView,
		onEnterKey
	},
	watch: {
		query: 'performAutoComplete'
	},
	created() {
		// Register event handlers for Search.vue to use to modify our state
		EventBus.$on( 'searchQueryChange', setQuery );
		EventBus.$on( 'searchQueryClear', () => {
			this.query = '';
			if ( this.$refs.combobox ) {
				this.$refs.combobox.reset();
			}
		} );
	}
};
</script>
