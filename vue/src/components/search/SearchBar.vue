<template>
	<v-combobox
		v-model="query"
		class="searchbar"
		:label="$t( 'search-label' )"
		:loading="loading || toolAutoCompleteLoading"
		:search-input.sync="query"
		:menu-props="menuProps"
		:items="getToolAutoCompleteResultsArr()"
		solo
		clearable
		hide-details
		@keyup.enter="onSearch"
		@change="routeToToolsView"
		@click:clear="onClear"
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
			<v-list-item-content>
				<v-list-item-title>
					<dl class="row ma-0">
						<dt class="me-1">{{ data.item }}</dt>
						<dd>({{ toolAutoCompleteResults[data.item] }})</dd>
					</dl>
				</v-list-item-title>
			</v-list-item-content>
		</template>

		<template v-if="!toolAutoCompleteLoading" #no-data>
			<v-list-item>
				<v-list-item-content>
					<v-list-item-title>
						{{ $t( 'tool-not-found', [ query ] ) }}
					</v-list-item-title>
				</v-list-item-content>
			</v-list-item>
		</template>
	</v-combobox>
</template>

<script>
import { mapState } from 'vuex';

function onSearch() {
	this.$emit( 'search', this.query );
}

function onClear() {
	this.query = '';
	this.$emit( 'search', this.query );
}

function setQuery( query ) {
	this.query = query;
}

function performToolAutoComplete( v ) {
	this.toolAutoCompleteLoading = true;
	const payload = {
		query: v
	};
	this.$store.dispatch( 'search/autoCompleteTools', payload ).finally(
		() => {
			this.toolAutoCompleteLoading = false;
		}
	);
}

function routeToToolsView( name ) {
	this.$router.push( { name: 'tools-view', params: { name } } );
}

function getToolAutoCompleteResultsArr() {
	return this.toolAutoCompleteResults ?
		Object.keys( this.toolAutoCompleteResults ) :
		[];
}

export default {
	name: 'SearchBar',
	props: {
		loading: {
			type: Boolean
		}
	},
	data: () => ( {
		query: '',
		toolAutoCompleteLoading: false
	} ),
	computed: {
		menuProps() {
			return !this.query ? { value: false } : {};
		},
		...mapState( 'search', {
			toolAutoCompleteResults: 'toolAutoCompleteResults'
		} )
	},
	methods: {
		onSearch,
		onClear,
		// eslint-disable-next-line vue/no-unused-properties
		setQuery,
		performToolAutoComplete,
		getToolAutoCompleteResultsArr,
		routeToToolsView
	},
	watch: {
		query: {
			handler( val ) {
				this.performToolAutoComplete( val );
			}
		}
	}
};
</script>
