<template>
	<v-combobox
		v-model="query"
		class="searchbar"
		:label="getLabel()"
		:loading="loading || autoCompleteLoading"
		:search-input.sync="query"
		:menu-props="menuProps"
		:items="getAutoCompleteResultsArr()"
		solo
		clearable
		hide-details
		@keyup.enter="onSearch"
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

function onSearch() {
	this.$emit( 'search', this.query );
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
		autoCompleteLoading: false
	} ),
	computed: {
		menuProps() {
			const contentClass = { contentClass: 'autocomplete-menu__content' };
			return !this.query ? { value: false, ...contentClass } : contentClass;
		},
		...mapState( 'search', {
			autoCompleteResults: function ( state ) {
				return state[ `${this.target}AutoCompleteResults` ];
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
		routeToView
	},
	watch: {
		query: {
			handler( val ) {
				this.performAutoComplete( val );
			}
		}
	}
};
</script>
