<template>
	<v-row
		v-if="$vuetify.breakpoint.mdAndUp"
		no-gutters
		dense
	>
		<v-col
			v-for="facet in displayedFacets"
			:key="facet.name"
			md="12"
			cols="6"
		>
			<FilterList
				v-model="value[ facet.name ]"
				:facet="facet"
				class="mb-2"
				outlined
			>
				<template #header>
					<v-card-title class="title accent flex-grow-0">
						<v-badge
							inline
							:value="facet.selected.length > 0"
							:content="facet.selected.length"
							color="info"
						>
							{{ renderFacetTitle( facet ) }}
						</v-badge>
					</v-card-title>
				</template>
			</FilterList>
		</v-col>
	</v-row>

	<v-slide-group
		v-else
		v-model="slide"
		show-arrows
		class="compact-arrows"
	>
		<v-slide-item
			v-for="facet in displayedFacets"
			:key="facet.name"
		>
			<v-dialog
				v-model="dialogs[ facet.name ]"
				fullscreen
				hide-overlay
				transition="dialog-bottom-transition"
			>
				<template #activator="{ on, attrs }">
					<v-btn
						class="mx-1 my-1"
						color="white"
						elevation="2"
						v-bind="attrs"
						v-on="on"
					>
						<v-badge
							inline
							:value="facet.selected.length > 0"
							:content="facet.selected.length"
							color="info"
						>
							{{ renderFacetTitle( facet ) }}
						</v-badge>
						<v-icon right>mdi-menu-down</v-icon>
					</v-btn>
				</template>
				<FilterList
					v-model="value[ facet.name ]"
					:facet="facet"
				>
					<template #header>
						<v-toolbar
							class="flex-grow-0"
							color="accent"
							flat
							tile
						>
							<v-toolbar-title class="title">
								{{ renderFacetTitle( facet ) }}
							</v-toolbar-title>
							<v-spacer />
							<v-btn
								icon
								@click="dialogs[ facet.name ] = false"
							>
								<v-icon>mdi-close-box-outline</v-icon>
							</v-btn>
						</v-toolbar>
					</template>
				</FilterList>
			</v-dialog>
		</v-slide-item>
	</v-slide-group>
</template>

<script>
import { ensureArray } from '@/utils';
import FilterList from '@/components/search/FilterList';

export const methods = {
	/**
	 * Decide if a facet should be rendered or not.
	 *
	 * @param {Object} facet
	 * @return {boolean}
	 */
	shouldShowFacet( facet ) {
		return facet.buckets.length > 0 &&
			!( facet.buckets.length === 1 &&
				facet.buckets[ 0 ].key === facet.missingValue &&
				facet.selected.length === 0
			);
	},

	/**
	 * Get title display string for a given facet.
	 *
	 * @param {Object} facet
	 * @return {string}
	 */
	renderFacetTitle( facet ) {
		// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
		return this.$i18n.t( this.getl10nTitleKey( facet ) );
	},

	/**
	 * Get a localization message key for the given facet's title.
	 *
	 * @param {Object} facet
	 * @return {string}
	 */
	getl10nTitleKey( facet ) {
		switch ( facet.name ) {
			case 'author':
			case 'keywords':
			case 'license':
			case 'tool_type':
			case 'ui_language':
			case 'wiki':
				return 'search-filter-' + facet.name.replace( /_/g, '-' );
			default:
				return facet.name;
		}
	}
};

export default {
	name: 'Filters',
	components: {
		FilterList
	},
	props: {
		facets: {
			type: Array,
			default: () => [],
			required: true
		}
	},
	data: () => ( {
		dialogs: {},
		slide: undefined,
		value: {}
	} ),
	computed: {
		/**
		 * Computed list of facets that should be displayed.
		 *
		 * @return {Object[]}
		 */
		displayedFacets() {
			return this.facets.filter(
				( facet ) => this.shouldShowFacet( facet )
			);
		}
	},
	methods: methods,
	watch: {
		/**
		 * Emit a 'change' event with a payload of query params when our state
		 * changes.
		 *
		 * @fires change
		 */
		value: {
			deep: true,
			handler( data ) {
				const filters = [];
				for ( const name in data ) {
					filters.push( ...ensureArray( data[ name ] ) );
				}
				const params = filters.filter( ( val ) => val !== null )
					.sort( ( a, b ) => a[ 0 ].localeCompare( b[ 0 ] ) );
				this.$emit( 'change', params );
			}
		}
	}
};
</script>
