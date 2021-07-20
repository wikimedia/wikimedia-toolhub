<template>
	<v-text-field
		v-model="query"
		class="searchbar"
		:label="$t( 'search-label' )"
		:loading="loading"
		solo
		clearable
		hide-details
		@keydown.enter="onSearch"
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
	</v-text-field>
</template>

<script>
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

export default {
	name: 'SearchBar',
	props: {
		loading: {
			type: Boolean
		}
	},
	data: () => ( {
		query: null
	} ),
	methods: {
		onSearch,
		onClear,
		setQuery
	}
};
</script>
