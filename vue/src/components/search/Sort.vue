<template>
	<v-select
		v-model="select"
		:items="items"
		return-object
		dense
		solo
		prepend-icon="mdi-sort"
		@change="onChange"
	>
		<template #item="{ item }">
			<!-- eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys -->
			{{ $t( item.label ) }}
		</template>
		<template #selection="{ item }">
			<!-- eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys -->
			{{ $t( item.label ) }}
		</template>
	</v-select>
</template>

<script>
export const methods = {
	/**
	 * Handle a change event from a list item group.
	 *
	 * @param {Object} value - currently selected value
	 * @fires change
	 */
	onChange( value ) {
		this.$emit( 'change', value );
	},

	/**
	 * Set the selected sort order.
	 *
	 * @param {string} value - sort order
	 */
	setOrder( value ) {
		this.select = this.items.find( ( e ) => e.value === value );
	}
};

export default {
	name: 'Sort',
	data: () => ( {
		items: [
			{
				label: 'search-sort-score',
				value: '-score'
			},
			{
				label: 'search-sort-created-asc',
				value: 'created_date'
			},
			{
				label: 'search-sort-created-desc',
				value: '-created_date'
			},
			{
				label: 'search-sort-modified-asc',
				value: 'modified_date'
			},
			{
				label: 'search-sort-modified-desc',
				value: '-modified_date'
			}
		],
		select: '-score'
	} ),
	methods
};
</script>
