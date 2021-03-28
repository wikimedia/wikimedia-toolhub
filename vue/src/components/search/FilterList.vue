<template>
	<v-card
		:outlined="outlined"
		class="d-flex flex-column"
		max-height="100%"
	>
		<slot name="header" />
		<v-card-text
			class="px-0 flex-grow-1 overflow-auto"
		>
			<v-list
				dense
				shaped
			>
				<v-list-item-group
					v-model="value"
					:multiple="facet.multi"
					color="primary"
					@change="updateModel"
				>
					<v-list-item
						v-for="bucket in facet.buckets"
						:key="bucket.key"
						:value="bucket.key"
					>
						<v-list-item-content>
							{{ renderBucketKey( bucket.key ) }}
						</v-list-item-content>
						<v-list-item-action>
							<v-chip outlined>
								{{ bucket.doc_count }}
							</v-chip>
						</v-list-item-action>
					</v-list-item>
				</v-list-item-group>
			</v-list>
		</v-card-text>
		<v-card-actions class="flex-grow-0">
			<v-btn
				v-if="facet.selected.length > 0"
				block
				@click="clearSelected"
			>
				<v-icon left>mdi-backspace-outline</v-icon>
				{{ $t( 'search-filter-clear-selected' ) }}
			</v-btn>
		</v-card-actions>
		<slot name="footer" />
	</v-card>
</template>

<script>
import { mapState } from 'vuex';
import { ensureArray } from '@/helpers/array';
import { forWikiLabel } from '@/helpers/tools';

export const methods = {
	/**
	 * Get display string for a given bucket value.
	 *
	 * @param {string} value
	 * @return {string}
	 */
	renderBucketKey( value ) {
		if ( value === this.facet.missingValue ) {
			return this.$i18n.t( 'search-filter-missing-value' );
		}
		if ( this.facet.name === 'ui_language' ) {
			return this.$i18n.t( 'search-filter-ui-language-value', [
				this.localeMap[ value ] || value,
				value
			] );
		}
		if ( this.facet.name === 'wiki' ) {
			return forWikiLabel( value );
		}
		if ( this.facet.name === 'tool_type' ) {
			// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
			return this.$i18n.t(
				'search-filter-tool-type-' + value.replace( /\s/g, '-' )
			);
		}
		if ( this.facet.name === 'origin' ) {
			// eslint-disable-next-line @intlify/vue-i18n/no-dynamic-keys
			return this.$i18n.t( 'search-filter-origin-' + value );
		}
		return value;
	},

	/**
	 * Build search filters for a term facet.
	 *
	 * @param {Object} facet
	 * @param {Array<string>} selected
	 * @return {string[][]} List of [key, value] query string parameters
	 */
	buildTermFilters( facet, selected ) {
		return selected.map( ( term ) => {
			if ( term === facet.missingValue ) {
				return [ facet.missingParam, 1 ];
			}
			return [ facet.param, term ];
		} );
	},

	/**
	 * Build a list of search filters based on selected facet values.
	 *
	 * @return {string[][]} List of [key, value] query string parameters
	 */
	buildFilters() {
		const fname = this.facet.name;
		const ftype = this.facet.type;
		const selected = ensureArray( this.value );
		let filters = [];
		switch ( ftype ) {
			case 'terms':
				filters = filters.concat(
					this.buildTermFilters( this.facet, selected )
				);
				break;
			default:
				throw TypeError(
					`Unknown type '${ftype}' for facet '${fname}'`
				);
		}
		return filters.sort( ( a, b ) => a[ 0 ].localeCompare( b[ 0 ] ) );
	},

	/**
	 * Handle a change event from a list item group by emitting a new
	 * 'change' event with a payload of query params.
	 *
	 * @fires change
	 */
	updateModel() {
		this.$emit( 'change', this.buildFilters() );
	},

	clearSelected() {
		this.value = this.facet.multi ? [] : null;
		this.updateModel();
	}
};

export default {
	name: 'FilterList',
	model: {
		prop: 'model',
		event: 'change'
	},
	props: {
		facet: {
			type: Object,
			default: () => {},
			required: true
		},
		outlined: Boolean
	},
	data: () => ( {
		model: undefined,
		value: undefined
	} ),
	computed: {
		...mapState( 'locale', [ 'localeMap' ] )
	},
	methods: methods,
	watch: {
		facet: {
			deep: true,
			immediate: true,
			handler( facet ) {
				// Set selection state
				this.value = facet.multi ?
					( facet.selected || null ) :
					( facet.selected[ 0 ] || null );
			}
		}
	}
};
</script>
